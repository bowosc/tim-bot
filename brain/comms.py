import requests
from requests import Response

TESTING = True



BASE = "host.docker.internal:8080" #"192.168.7.227" #"http://192.168.4.1" # ESP32 web server ip

def send_cmd(cmd: str, timeout: int = 2) -> Response:
    '''
    Sends a command to the ESP32 over HTTP.

    :param str cmd: Command instruction. This will go after the / in the HTTP request.
    :param int timeout: Timeout for waiting for a response.

    :return Response: HTTP response from ESP32. 
    '''

    if TESTING:
        print(f"Sent cmd {cmd}.")
        return
    
    url = f"http://{BASE}/{cmd}" # not https
    r = requests.get(url, timeout=timeout)
    #print("Response:", r.status_code, r.text)
    return r

