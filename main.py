import machine, neopixel, utime, os, time, sys
import ujson
from machine import Pin
from pico_lte.utils.status import Status
from pico_lte.core import PicoLTE
from pico_lte.common import debug
from printer import printMessage

# Uncomment this for verbose logging
debug.set_level(0)

# Constants
USER_LED = Pin(22, mode=Pin.OUT)
NEOPIXEL_NUM_LEDS = 8
NEOPIXEL_PIN = machine.Pin(15)
NEOPIXEL_RUN_TIME_SECONDS = 2
MAIN_LOOP_DELAY_SECONDS = 1800 # 30 minute loop delay

# Variables
picoLTE = PicoLTE()
neopixel = neopixel.NeoPixel(NEOPIXEL_PIN, NEOPIXEL_NUM_LEDS)
light_up_neopixel = False            
readDelay = 15
run_count = 0
request_failures = 0

# Sets all NeoPixel LEDs off
def set_neopixel_off():
    for i in range(NEOPIXEL_NUM_LEDS):
        neopixel[i] = (0, 0, 0)
    neopixel.write()

def neopixel_color_cycle(wait):
    for i in range(NEOPIXEL_NUM_LEDS):
        neopixel[i] = (255, 0, 0)  # Set LED color to red
    neopixel.write()
    utime.sleep_ms(wait)
    
    for i in range(NEOPIXEL_NUM_LEDS):
        neopixel[i] = (0, 255, 0)  # Set LED color to green
    neopixel.write()
    utime.sleep_ms(wait)
    
    for i in range(NEOPIXEL_NUM_LEDS):
        neopixel[i] = (0, 0, 255)  # Set LED color to blue
    neopixel.write()
    utime.sleep_ms(wait)

# Turns LEDs off, checks local data file, logs ambient temperature, and registers LTE network
def run_initial_setup():
    # Turn off all LEDs
    set_neopixel_off();
    USER_LED.off()

    # Initialize file system as needed
    print("run_initial_setup: Reading root directory... ****")
    print(os.listdir())
    initial_file = open("data.txt", "a")
    data = initial_file.read()
    print("\run_initial_setup: Data file content:")
    if not data:
        print("run_initial_setup: NO DATA FOUND")
    else:
        print(data)
    initial_file.close()

    # Log ambient temperature for fun
    print("run_initial_setup: Reading ambient temperature... ****")
    sensor_temp = machine.ADC(4)
    conversion_factor = 3.3 / (65535)
    reading = sensor_temp.read_u16() * conversion_factor
    temp = 27 - (reading -0.706)/(0.001721)
    print(temp)

    # Get LTE system ready
    print("run_initial_setup: Registering LTE network... ****")
    picoLTE.network.register_network()
    picoLTE.http.set_context_id()
    picoLTE.network.get_pdp_ready()
    picoLTE.http.set_server_url()

# Check if the response message matches the one in the data file. If not, we should print it
def check_if_should_print(extracted_message):
    print("check_if_should_print(" + extracted_message + ") ****")
    file = open("data.txt", "r+")
    file_message = file.read()
    if extracted_message != file_message:
        print("check_if_should_print: File data is '" + file_message + "', which doesn't match ****")
        file.write(extracted_message)
        file.close()
        return True
    else:
        print("check_if_should_print: File data is '" + file_message + "' which matches latest message ****")
        file.close()
        return False

# Parse the response for the message, check if it matches the data file, and print if it doesn't
def parse_and_try_print(message):
    try:
        print("parse_and_try_print: Checking response message of: '" + message + "' ****")
        should_print = check_if_should_print(message)
        if should_print:
            # Light up the NeoPixel for a few cycles
            neopixel_cycle_count = 0
            while neopixel_cycle_count < (NEOPIXEL_RUN_TIME_SECONDS * 10):
                neopixel_color_cycle(100)
                neopixel_cycle_count += 1
            set_neopixel_off();
            # Print the message
            print("parse_and_try_print: Printing message... ****")
            printMessage(message)
    except:
        print("parse_and_try_print: Exception occurred while parsing response! ****")
        set_neopixel_off()
        
class WebResponse(object):
    def __init__(self, json_str):
        data = ujson.loads(json_str)
        for key, value in data.items():
            setattr(self, key, value)

# Run the initial setup and then keep sending requests (main loop)
try:
    print("main_loop: Initial setup starting... ****")
    run_initial_setup()
    print("main_loop: Initial setup complete... ****")
    while True:
        USER_LED.on()
        # Reset the HTTP context before making a new request
        picoLTE.http.set_context_id()
        picoLTE.network.get_pdp_ready()
        picoLTE.http.set_server_url()
        print("main_loop: Sending web request... ****")
        result = picoLTE.http.get()
        time.sleep(readDelay)

        # After the delay, read response. This gives the Sixfab LTE time to process the request
        result = picoLTE.http.read_response()
        debug.info(result)

        # Check if the response was successful
        if result["status"] == Status.SUCCESS:
            json_result = ujson.dumps(result)
            if len(json_result) > 250:
                # This seems excessively long, is this a 404 page?
                print("main_loop: Got a response longer than max characters! Not going to print!")
                readDelay = 30
                request_failures += 1
            else:
                # Looks good, reset delay to the default
                print("main_loop: Got what looks like a good response")
                readDelay = 15
                request_failures = 0
                webby = WebResponse(json_result)
                parse_and_try_print(webby.response[1])
        else:
            # No dice, extend delay before reading response. Try again next time
            readDelay = 30
            request_failures += 1
        
        # Get ready for the next loop
        USER_LED.off()
        run_count += 1
        if run_count > 24:
            print("main_loop: Reached run count threshold, resetting device...")
            machine.reset()
        elif request_failures > 2:
            print("main_loop: Too many request failures, resetting device...")
            machine.reset()
        
        # Wait this many seconds before running the loop again
        time.sleep(MAIN_LOOP_DELAY_SECONDS)
except Exception as e:
    sys.print_exception(e)
    print("main_loop: Exception occurred! Cleaning up... ****")
    light_up_neopixel = False
    set_neopixel_off()
    USER_LED.off()

print("\n**** Program Exiting ****")
machine.reset()
