import machine, neopixel, utime, os, time, sys
from machine import Pin
from pico_lte.utils.status import Status
from pico_lte.core import PicoLTE
from pico_lte.common import debug
from printer import printMessage

# Uncomment this for verbose logging
#debug.set_level(0)

printMessage("Hi there! Setting things up...")

# Constants
USER_LED = Pin(22, mode=Pin.OUT)
NEOPIXEL_NUM_LEDS = 8
NEOPIXEL_PIN = machine.Pin(15)
MAIN_LOOP_DELAY_SECONDS = 30

# Variables
neopixel = neopixel.NeoPixel(NEOPIXEL_PIN, NEOPIXEL_NUM_LEDS)
showRainbow = False            
readDelay = 5
        
# Sets all NeoPixel LEDs off
def set_neopixel_off():
    for i in range(NEOPIXEL_NUM_LEDS):
        neopixel[i] = (0, 0, 0)
    neopixel.write()

# Turns LEDs off, checks local data file, logs ambient temperature, and registers LTE network
def run_initial_setup():
    # Turn off all LEDs
    set_neopixel_off();
    USER_LED.off()

    # Initialize file system as needed
    print("\n**** Reading root directory... ****")
    print(os.listdir())
    initial_file = open("data.txt", "a")
    data = initial_file.read()
    print("\n**** Data file content:")
    if not data:
        print("NO DATA FOUND")
    else:
        print(data)
    initial_file.close()

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

# Check if the response message matches the one in the data file. If not, we should print it
def check_if_should_print(extracted_message):
    print("\n**** check_file_against_message(" + extracted_message + ") ****")
    file = open("data.txt", "r")
    file_message = file.read()
    messages_differ = extracted_message != file_message
    if messages_differ:
        file.write(extracted_message, "w")
    file.close()
    return messages_differ

# Parse the response for the message, check if it matches the data file, and print if it doesn't
def parse_and_try_print(response):
    try:
        print("\n**** parse_and_try_print(" + response + ") ****")
        response_parts = response.split("\"")
        print(response_parts)
        extracted_message = response_parts[1]
        print("Checking response message of: '" + extracted_message + "'")
        should_print = check_if_should_print(extracted_message)
        if should_print:
            light_up_neopixel = True
            print("\n**** Printing message... ****")
            printMessage(response)
            light_up_neopixel = False
    except:
        print("\n**** Exception occurred while parsing response! ****")
        light_up_neopixel = False

# Run the initial setup and then keep sending requests (main loop)
try:
    run_initial_setup()
    while True:
        USER_LED.on()
        result = picoLTE.http.get()
        print("\n**** Done! (" + result + "). Will read response shortly... ****")
        time.sleep(readDelay)
        # After the delay, read response. This gives the Sixfab LTE time to process the request
        result = picoLTE.http.read_response()
        debug.info(result)
        # Check if the response was successful
        if result["status"] == Status.SUCCESS:
            # Looks good, reset delay to the default
            readDelay = 5
            parse_and_try_print(result)
        else:
            # No dice, extend delay before reading response. Try again next time
            readDelay = 15
        USER_LED.off()
        # Wait this many seconds before running the loop again
        time.sleep(MAIN_LOOP_DELAY_SECONDS)
except:
    print("\n**** Exception occurred! Cleaning up... ****")
    light_up_LEDs = False
    set_neopixel_off()
    USER_LED.off()

print("\n**** Program Exiting ****")
sys.exit()