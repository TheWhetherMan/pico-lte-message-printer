import machine, neopixel, utime, os, time, sys
from machine import Pin
from pico_lte.utils.status import Status
from pico_lte.core import PicoLTE
from pico_lte.common import debug
from printer import printMessage

# Uncomment this for verbose logging
#debug.set_level(0)

printMessage("Hi there! Setting things up...")

def set_neopixel_off():
    for i in range(NEOPIXEL_NUM_LEDS):
        neopixel[i] = (0, 0, 0)
    neopixel.write()

# Definitions and signatures
USER_LED = Pin(22, mode=Pin.OUT)
NEOPIXEL_NUM_LEDS = 8
NEOPIXEL_PIN = machine.Pin(15)
neopixel = neopixel.NeoPixel(NEOPIXEL_PIN, NEOPIXEL_NUM_LEDS)
showRainbow = False            
readDelay = 5

def parseAndPrint(response):
    shouldPrint = True
    if shouldPrint:
        showRainbow = True
        print("\n**** Printing message... ****")
        printMessage(response)
        showRainbow = False
        
# Set NeoPixel LEDs and user LED off
set_neopixel_off();
USER_LED.off()
    
# Initialize file system as needed
print("\n**** Reading root directory... ****")
print(os.listdir())
f = open("data.txt", "a")
data = f.read()
print("\n**** Data file content:")
if not data:
    print("NO DATA FOUND")
else:
    print(data)
f.close()

# Log ambient temperature for fun
print("\n**** Reading ambient temperature... ****")
sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535)
reading = sensor_temp.read_u16() * conversion_factor
temp = 27 - (reading -0.706)/(0.001721)
print(temp)

# Reach out to web for data
print("\n**** Registering LTE network... ****")
picoLTE = PicoLTE()
picoLTE.network.register_network()
picoLTE.http.set_context_id()
picoLTE.network.get_pdp_ready()
picoLTE.http.set_server_url()
print("\n**** Ready to send requests... ****")

try:        
    while True:
        USER_LED.on()
        result = picoLTE.http.get()
        debug.info(result)

        print("\n**** Done, will read response shortly... ****")
        time.sleep(readDelay)
        result = picoLTE.http.read_response()
        debug.info(result)
        if result["status"] == Status.SUCCESS:
            # Looks good, reset delay
            readDelay = 5
            parseAndPrint(result)
        else:
            # No dice, extend delay before reading response
            readDelay = 15
        USER_LED.off()
except:
    print("\n**** Exception occurred! Cleaning up... ****")
    set_neopixel_off()
    USER_LED.off()

print("\n**** Program Exiting ****")
sys.exit()