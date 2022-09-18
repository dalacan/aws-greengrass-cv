import sys
import traceback
import json
import time

import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    SubscriptionResponseMessage,
    UnauthorizedError
)
# TO DO: Make this configurable
topic = 'devices/ObjectState'

class StreamHandler(client.SubscribeToTopicStreamHandler):
    def __init__(self):
        super().__init__()
        self.object_state = {}

    def on_stream_event(self, event: SubscriptionResponseMessage) -> None:
        try:
            print("Receiving message")
            message = event.json_message.message
            topic = event.json_message.context.topic
            print('Received new message on topic %s: %s' % (topic, message))

            print("CameraId: {}".format(message["cameraId"]))
            print("objectState: {}".format(message["objectState"]))

            self.set_object_state(message)
        except:
            traceback.print_exc()

    def on_stream_error(self, error: Exception) -> bool:
        print('Received a stream error.', file=sys.stderr)
        traceback.print_exc()
        return False  # Return True to close stream, False to keep stream open.

    def on_stream_closed(self) -> None:
        print('Subscribe to topic stream closed.')

    def set_object_state(self, message):
        print("Setting object state")
        self.object_state[message["cameraId"]] = message["objectState"]