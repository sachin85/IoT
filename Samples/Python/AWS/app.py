from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json
import random

host = "<<host>>"
certPath = "F:/Learning/Training/IoT Training/AwsIoT/Demo/demo-cert/"
clientId = "Device1"
topic = "demo-topic"
TEMPERATURE = 20.0
HUMIDITY = 60

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureEndpoint(host, 8883)
myAWSIoTMQTTClient.configureCredentials("{}aws-root-cert.pem".format(certPath), "{}private-key.pem.key".format(certPath), "{}iot-cert.pem.crt".format(certPath))
# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
myAWSIoTMQTTClient.configureUsernamePassword("sachin")
myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.subscribe("Pratik", 1, customCallback)

# Publish to the same topic in a loop forever
loopCount = 0
while True:
    message = {}
    message['DeviceId'] = "Device1"
    message['Name'] = "Sachin"
    message['temperature'] = TEMPERATURE + (random.random() * 15)
    message['humidity'] = HUMIDITY + (random.random() * 20)
    messageJson = json.dumps(message)
    myAWSIoTMQTTClient.publish(topic, messageJson, 1)
    print('Published topic %s: %s\n' % (topic, messageJson))
    loopCount += 1
    time.sleep(10)
myAWSIoTMQTTClient.disconnect()
