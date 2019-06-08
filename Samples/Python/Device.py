import random
import time
import sys

import iothub_client
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue

CONNECTION_STRING = "HostName=IoTDemoClass.azure-devices.net;DeviceId=Device1;SharedAccessKey=68Z04SYT67d/2e2OhnkVp3bvPrUM0cRErxaYRWlpv+k="

PROTOCOL = IoTHubTransportProvider.MQTT
MESSAGE_TIMEOUT = 10000
RECEIVE_CONTEXT = 0
WAIT_COUNT = 10
RECEIVED_COUNT = 0
RECEIVE_CALLBACKS = 0

TEMPERATURE = 20.0
HUMIDITY = 60
MSG_TXT = "{\"temperature\": %.2f,\"humidity\": %.2f}"
TIMER_COUNT = 5
TWIN_CONTEXT = 0
SEND_REPORTED_STATE_CONTEXT = 0
INTERVAL = 10

def send_confirmation_callback(message, result, user_context):
    print ( "IoT Hub responded to message with status: %s" % (result) )

def iothub_client_init():
    # Create an IoT Hub client
    client = IoTHubClient(CONNECTION_STRING, PROTOCOL)
    return client

def print_last_message_time(client):
    try:
        last_message = client.get_last_message_receive_time()
        print ( "Last Message: %s" % time.asctime(time.localtime(last_message)) )
        print ( "Actual time : %s" % time.asctime() )
    except IoTHubClientError as iothub_client_error:
        if iothub_client_error.args[0].result == IoTHubClientResult.INDEFINITE_TIME:
            print ( "No message received" )
        else:
            print ( iothub_client_error )

def receive_message_callback(message, counter):
    global RECEIVE_CALLBACKS
    message_buffer = message.get_bytearray()
    size = len(message_buffer)
    print ( "Received Message [%d]:" % counter )
    print ( "    Data: <<<%s>>> & Size=%d" % (message_buffer[:size].decode('utf-8'), size) )
    map_properties = message.properties()
    key_value_pair = map_properties.get_internals()
    print ( "    Properties: %s" % key_value_pair )
    counter += 1
    RECEIVE_CALLBACKS += 1
    print ( "    Total calls received: %d" % RECEIVE_CALLBACKS )
    return IoTHubMessageDispositionResult.ACCEPTED

# Handle direct method calls from IoT Hub
def device_method_callback(method_name, payload, user_context):
    global INTERVAL
    print ( "\nMethod callback called with:\nmethodName = %s\npayload = %s" % (method_name, payload) )
    device_method_return_value = DeviceMethodReturnValue()
    if method_name == "SetTelemetryInterval":
        try:
            INTERVAL = int(payload)
            # Build and send the acknowledgment.
            device_method_return_value.response = "{ \"Response\": \"Executed direct method %s\" }" % method_name
            device_method_return_value.status = 200
        except ValueError:
            # Build and send an error response.
            device_method_return_value.response = "{ \"Response\": \"Invalid parameter\" }"
            device_method_return_value.status = 400
    else:
        # Build and send an error response.
        device_method_return_value.response = "{ \"Response\": \"Direct method not defined: %s\" }" % method_name
        device_method_return_value.status = 404
    return device_method_return_value

def blob_upload_conf_callback(result, user_context):
    if str(result) == 'OK':
        print ( "...file uploaded successfully." )
    else:
        print ( "...file upload callback returned: " + str(result) )

def iothub_client_telemetry_sample_run():
    try:
        client = iothub_client_init()
        print ( "IoT Hub device sending periodic messages, press Ctrl-C to exit" )

        # Set up the callback method for direct method calls from the hub.
        client.set_device_method_callback(
            device_method_callback, None)

        client.set_message_callback(receive_message_callback, RECEIVE_CONTEXT)       

        while True:
            # Build the message with simulated telemetry values.
            temperature = TEMPERATURE + (random.random() * 15)
            humidity = HUMIDITY + (random.random() * 20)
            msg_txt_formatted = MSG_TXT % (temperature, humidity)
            message = IoTHubMessage(msg_txt_formatted)

            prop_map = message.properties()
            if temperature > 30:
              prop_map.add("temperatureAlert", "true")
            else:
              prop_map.add("temperatureAlert", "false")
            # Send the message.
            print( "Sending message: %s" % message.get_string() )
            client.send_event_async(message, send_confirmation_callback, None)            
            time.sleep(INTERVAL)

    except IoTHubError as iothub_error:
        print ( "Unexpected error %s from IoTHub" % iothub_error )
        return
    except KeyboardInterrupt:
        print ( "IoTHubClient sample stopped" )

if __name__ == '__main__':
    print ( "IoT Hub Quickstart #2 - Simulated device" )
    print ( "Press Ctrl-C to exit" )
    iothub_client_telemetry_sample_run()
