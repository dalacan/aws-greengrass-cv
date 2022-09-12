import glob
import os
import sys
import traceback
import json
import cv2


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

    def compare_image(self, comparison_image):
        base_image = '/tmp/base_image.jpg'
        base_image = cv2.imread(base_image)
        base_image = cv2.cvtColor(base_image, cv2.COLOR_BGR2RGB)
        base_image_hist = cv2.calcHist([base_image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        base_image_hist = cv2.normalize(hist, hist).flatten()

        comparison_image = cv2.cvtColor(comparison_image, cv2.COLOR_BGR2RGB)

        hist = cv2.calcHist([comparison_image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        hist = cv2.normalize(hist, hist).flatten()

        OPENCV_METHODS = (
            ("Correlation", cv2.HISTCMP_CORREL),
            ("Chi-Squared", cv2.HISTCMP_CHISQR),
            ("Intersection", cv2.HISTCMP_INTERSECT),
            ("Hellinger", cv2.HISTCMP_BHATTACHARYYA))

        # loop over the comparison methods
        for (methodName, method) in OPENCV_METHODS:
            # compute the distance between the two histograms
            # using the method and update the results dictionary
            base_image_distance = cv2.compareHist(base_image_hist, base_image_hist, method)
            distance = cv2.compareHist(base_image_hist, hist, method)

            print("Method Name: {} base_image_distance: {}, comparison distance: {}".format(methodName, base_image_distance, distance))

    def run(self, object_state):
        # Get list of images from working directory
        images = glob.glob(self.working_directory + '/*.jpg')

        print(images)

        for idx, image in enumerate(images):
            # load image
            file_name = os.path.basename(image)
            camera_id = os.path.splitext(file_name)[0]
            print("Loading camera {}".format(camera_id))

            # get camera state
            if camera_id in object_state:
                print("Camera state found")
            else:
                print("Camera state not found, assume 0")

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


def fake_detector():
    # Detector output
    # 0 - No object
    # 1 - Object found
    return 1

def publish_json_message_to_topic(ipc_client, topic, message):
    print("Creating json message")
    json_message = JsonMessage(message=message)

    print("Publish message")
    publish_message = PublishMessage(json_message=json_message)
    
    print("Publish to topic")
    return ipc_client.publish_to_topic(topic=topic, publish_message=publish_message)