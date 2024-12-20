"""
Example code for performing GET request to a server with using HTTP.

Example Configuration
---------------------
Create a config.json file in the root directory of the PicoLTE device.
config.json file must include the following parameters for this example:

config.json
{
    "https":{
        "server":"[HTTP_SERVER]",
        "username":"[YOUR_HTTP_USERNAME]",
        "password":"[YOUR_HTTP_PASSWORD]"
    },
}
"""

import time
from pico_lte.utils.status import Status
from pico_lte.core import PicoLTE
from pico_lte.common import debug

debug.set_level(0)
debug.info("Registering...")
picoLTE = PicoLTE()

picoLTE.network.register_network()
picoLTE.http.set_context_id()
picoLTE.network.get_pdp_ready()
# Uncomment the line below if you use basic HTTP authentication with username and password given in config.json file.
# picoLTE.http.set_auth()
picoLTE.http.set_server_url()

while True:
    debug.info("Sending a GET request.")
    result = picoLTE.http.get()
    debug.info(result)
    # Read the response after X seconds.
    time.sleep(15)
    result = picoLTE.http.read_response()
    debug.info(result)
    if result["status"] == Status.SUCCESS:
        debug.info("Get request succeeded.")

