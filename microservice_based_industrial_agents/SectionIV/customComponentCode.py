import json
import math
import os, requests
from threading import Thread

from flask import Flask, request

function = os.environ.get('SERVICE')
inPortNumber = os.environ.get('INPORT_NUMBER')

output = os.environ.get('OUTPUT')
output_port = os.environ.get('OUTPUT_PORT')

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def main():
    print(request)

    # First, we'll get the data from the HTTP message
    messageData = None
    if request.method == 'GET':
        # Handle GET requests
        return "You submitted a GET method!"
    elif request.method == 'POST':
        # Handle POST requests
        if "text/plain" in request.headers.get("Content-Type"):
            messageData = request.get_data(as_text=True)

    thread_func = None  # We use the new thread to send the "OK" message to the previous component as soon as possible, without blocking this component.
    match function:
        case "SquareRoot":
            thread_func = Thread(target=square_root, args=(messageData,))
        # TODO: Place your code here
        case "AintzaneFunction":
            thread_func = Thread(target=AintzaneMethod, args=(messageData,))    # TODO: Change your functionality method name here
        case _:
            return "No function selected"
    # The selected functionality is started in a new thread of execution
    thread_func.start()
    # Response to the previous component saying that everything went well
    return "OK\n"


'''
Functionality execution methods
'''
def square_root(messageData):
    # Get the value from the data sent in the HTTP message
    jsonData = json.loads(messageData)
    type = jsonData['type']
    value = jsonData['value']

    # If the entered step is of a different type, the result may be different, so we will make sure
    match type:
        case "natural" | "integer":
            value = int(value)
        case "float":
            value = float(value)
        case _:
            pass

    # Perform the mathematical function
    result = math.sqrt(value)

    if (type == "natural") or (type == "integer"):
        result = int(result)

    # Having the result, it will be passed to the next component
    sendData(type, result)


def AintzaneMethod(messageData): # TODO: Change your functionality method name here
    # Get the value from the data sent in the HTTP message
    jsonData = json.loads(messageData)
    type = jsonData['type']
    value = jsonData['value']

    # If the entered step is of a different type, the result may be different, so we will make sure
    match type:
        case "natural" | "integer":
            value = int(value)
        case "float":
            value = float(value)
        case _:
            pass

    # Perform the mathematical function
    # TODO: Place your code here
    result = value**3;

    # Having the result, it will be passed to the next component
    sendData(type, result)


def sendData(type, value):
    url = 'http://' + output + ':' + output_port
    headers = {'Content-Type': 'text/plain'}
    try:
        r = requests.post(url, headers=headers, data='{"type": "' + type + '", "value": ' + str(value) + '}')
        print(r.text)
    except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
        print("ERROR!!! The message could not be sent")
        print(e)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=inPortNumber)
