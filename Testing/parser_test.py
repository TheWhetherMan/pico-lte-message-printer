import ujson
import sys

class WebResponse(object):
    def __init__(self, json_str):
        data = ujson.loads(json_str)
        for key, value in data.items():
            setattr(self, key, value)

def check_if_should_print(extracted_message):
    print("check_file_against_message(" + extracted_message + ") ****")
    file = open("data.txt", "w")
    file_message = file.read()
    print("check_file_against_message: File data is '" + file_message + "' ****")
    if extracted_message != file_message:
        file.write(extracted_message)
        file.close()
        return True
    else:
        file.close()
        return False

def parse_and_try_print(message):
    print("Checking response message of: '" + message + "'")
    should_print = check_if_should_print(message)
    if should_print:
        light_up_neopixel = True
        print("\n**** Printing message... ****")
        printMessage(message)
        light_up_neopixel = False
        
result = {'response': ['+QHTTPGET: 0,200', 'A short but interesting message!', 'OK', '+QHTTPREAD: 0'], 'status': 0}
json_result = ujson.dumps(result)
print(json_result)
webby = WebResponse(json_result)
print(webby)
print(webby.response[1])
parse_and_try_print(webby.response[1])
