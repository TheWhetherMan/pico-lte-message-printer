from machine import UART, Pin
import time

USER_LED = Pin(22, mode=Pin.OUT)
    
def printMessage(message):
    print("\n****************************")
    print("**** PRINT JOB STARTING ****")
    print("****************************")
    USER_LED.on()
    uart = UART(1)
    uart.init(baudrate=19200, tx=Pin(4), rx=Pin(5))
    uart.write("\n")
    uart.write("\n")
    uart.write("\n")
    uart.write((str(message)).encode('cp437', 'ignore'))
    uart.write("\n")
    uart.write("\n")
    uart.write("\n")
    uart.write("\n")
    uart.write("\n")
    time.sleep(2);
    USER_LED.off()
    print("\n****************************")
    print("**** PRINT JOB COMPLETED ***")
    print("****************************")

#printMessage("Hello there!")
#printMessage("General Kenobi!")
