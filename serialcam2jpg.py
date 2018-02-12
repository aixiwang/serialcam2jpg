#---------------------------------------------------------
# serialcam2jpg
# -- a python tool to read jpeg image from chip VC0706.
# Tested with PTC01A RS485 interface camera 
# (https://item.taobao.com/item.htm?spm=a230r.1.14.22.bc7c3a5fWJTIAL&id=42069645143&ns=1&abbucket=1#detail)
#
# BSD 3-clause license is applied to this code
# Copyright(c) 2015 by Aixi Wang <aixi.wang@hotmail.com>
#---------------------------------------------------------
import serial
import thread
import time
import os
import sys


serial_s = None

print 'sys.argv[1]:',sys.argv[1]

        
#------------------------------------------
# common utils routines
#------------------------------------------
def readfile(filename):
    f = file(filename,'rb')
    fs = f.read()
    f.close()
    return fs

def writefile(filename,content):
    f = file(filename,'wb')
    fs = f.write(content)
    f.close()
    return
    
def has_file(filename):
    if os.path.exists(filename):
        return True
    else:
        return False
        
def remove_file(filename):
    if has_file(filename):
        os.remove(filename)
    
#----------------------
# ser_task
#----------------------
def ser_task():
    global serial_s
    print 'ser_task thread starting...'

    try:
        SERIAL_DEV_PATH = sys.argv[1]
    except:
        SERIAL_DEV_PATH = 'COM2'
       
    print 'serial port:',SERIAL_DEV_PATH
    
    while True:
        # wait for serial
        while True:
            try:
                serial_s = serial.Serial(SERIAL_DEV_PATH, 38400, timeout=0,parity='N',stopbits=1,xonxoff=0,rtscts=0)
                break;
            except:
                print 'waiting to reconnect serial port ...'                
                time.sleep(5)

        state = 0
        jpg_bin = ''
        while True:
            #print '>'
            try:
            #if 1:
                c1 = serial_s.read(1024)
                if len(c1) > 0:
                    #print 'c1:',c1
                    i = c1.find('\xff\xd8')
                    if  i>= 0:
                        jpg_bin = c1[i:]
                        state = 1
                        print '==========> JPG'
                        continue
                    
                    j = c1.find('\xff\xd9')                        
                    if j >= 0:
                        print '==========< JPG'                    
                        if state == 1:
                            jpg_bin += c1[:j+2]
                            writefile('now.jpg',jpg_bin)
                            state = 2
                            return
                    else:
                        if state == 1:
                            jpg_bin += c1

            except:
                print 'exception...1'
                serial_s.close()
                time.sleep(1)
                break


#----------------------
# start_ser_thread
#----------------------            
def start_ser_thread():
    thread.start_new_thread(ser_task,())
    
def module_reset(serial_s):
    print 'module_reset'
    serial_s.write('\x56\x00\x26\x00')

def module_snapshot(serial_s):
    print 'module_snapshot'
    serial_s.write('\x56\x00\x36\x01\x00')
    
def module_stop(serial_s):
    print 'module_stop'
    serial_s.write('\x56\x00\x36\x01\x03')

def module_read_pic_size(serial_s):
    print 'module_read_pic_size'
    serial_s.write('\x56\x00\x34\x01\x00')
    # return 76 00 34 00 04 00 00 XX xx
    
def module_read_pic_data(serial_s):
    print 'module_read_pic_data'
    serial_s.write('\x56\x00\x32\x0C\x00\x0A\x00\x00\x00\x00\x00\x00\xFF\xFF\x00\x00')
    
def module_set_picsize_320_240(serial_s):
    print 'module_set_picsize_320_240'
    serial_s.write('\x56\x00\x31\x05\x04\x01\x00\x19\x11')

def module_set_picsize_640_480(serial_s):
    print 'module_set_picsize_640_480'
    serial_s.write('\x56\x00\x31\x05\x04\x01\x00\x19\x00')
   
#------------------------------------------
# Main
#------------------------------------------
if __name__ == "__main__":
    start_ser_thread()
    while True:
        try:
            while(serial_s == None):
                print 'no available opened port\r\n'
                time.sleep(1)
            print '----------------------------------'
            print 'serial port has been opened'
            module_reset(serial_s)
            time.sleep(1)
            module_set_picsize_320_240(serial_s)
            time.sleep(1)    
            module_snapshot(serial_s)
            time.sleep(1)
            module_read_pic_data(serial_s)
            #module_stop(serial_s)
            print 'sleeping...'
            time.sleep(30)
        except Exception as e:
            print 'exception:',str(e)
            pass