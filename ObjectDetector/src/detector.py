import glob
import os
import sys
import traceback
import json


from awsiot.greengrasscoreipc.clientv2 import GreengrassCoreIPCClientV2
from awsiot.greengrasscoreipc.model import (
    PublishMessage,
    JsonMessage
)

# TO DO: Make this configurable
topic = 'devices/ObjectState'

class detector():
    def __init__(self, working_directory):
        self.working_directory = working_directory

    def load_model(self):
        # load the detector model
        print("Loading model")
    
    def get_camera_state(self, camera_id):
        print("Getting camera state for camera {}".format(camera_id))

    def run(self):
        # Get list of images from working directory
        images = glob.glob(self.working_directory + '/*.jpg')

        print(images)

        for idx, image in enumerate(images):
            # load image
            file_name = os.path.basename(image)
            camera_id = os.path.splitext(file_name)[0]
            print("Loading camera {}".format(camera_id))

            # get camera state

            # run detector only if state is 0 - no object or 2 object detected and processed

            # update state if required
            message = {"cameraId": camera_id,
               "objectState": 0}
            # message_json = json.dumps(message).encode('utf-8')

            try:
                ipc_client = GreengrassCoreIPCClientV2()
                publish_json_message_to_topic(ipc_client, topic, message)
                print('Successfully published to topic: ' + topic)
            except Exception:
                print('Exception occurred', file=sys.stderr)
                traceback.print_exc()
                exit(1)

        # run detector


def publish_json_message_to_topic(ipc_client, topic, message):
    print("Creating json message")
    json_message = JsonMessage(message=message)

    print("Publish message")
    publish_message = PublishMessage(json_message=json_message)
    
    print("Publish to topic")
    return ipc_client.publish_to_topic(topic=topic, publish_message=publish_message)