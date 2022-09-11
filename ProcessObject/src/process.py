import sys
import traceback
import cv2
import os
from pyzbar import pyzbar

import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    SubscriptionResponseMessage
)
# TO DO: Make this configurable
topic = 'devices/ObjectState'

class Process(client.SubscribeToTopicStreamHandler):
    def __init__(self, working_directory):
        super().__init__()
        self.working_directory = working_directory

    def on_stream_event(self, event: SubscriptionResponseMessage) -> None:
        try:
            print("Receiving message")
            message = event.json_message.message
            topic = event.json_message.context.topic
            print('Received new message on topic %s: %s' % (topic, message))

            print("CameraId: {}".format(message["cameraId"]))
            print("objectState: {}".format(message["objectState"]))

            # Do barcode scan
            print("Processing image")
            # TO DO: Add condition base on object state
            process_image(message["cameraId"], self.working_directory)
        except:
            traceback.print_exc()

    def on_stream_error(self, error: Exception) -> bool:
        print('Received a stream error.', file=sys.stderr)
        traceback.print_exc()
        return False  # Return True to close stream, False to keep stream open.

    def on_stream_closed(self) -> None:
        print('Subscribe to topic stream closed.')

def process_image(camera_id, working_directory):
    image_name = str(camera_id) + '.jpg'
    print("Reading ", os.path.join(working_directory, image_name))
    img = cv2.imread(os.path.join(working_directory, image_name))

    # Get barcodes from image
    print("Getting barcodes")
    barcodes = pyzbar.decode(img)

    print("barcodes: ".format(len(barcodes)))

    for barcode in barcodes:
        # extract the bounding box location of the barcode and draw the
        # bounding box surrounding the barcode on the image
        (x, y, w, h) = barcode.rect
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        # the barcode data is a bytes object so if we want to draw it on
        # our output image we need to convert it to a string first
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type
        # draw the barcode data and barcode type on the image
        text = "{} ({})".format(barcodeData, barcodeType)
        cv2.putText(img, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        # print the barcode type and data to the terminal
        print("[INFO] Found {} barcode: {} on camera {}".format(barcodeType, barcodeData, str(camera_id)))


def resize(img):
    print("Resizing image")

def save_to_s3(img, bucket):
    print("Saving to s3")

def save_to_folder(img, destination):
    print("Saving to folder")

  