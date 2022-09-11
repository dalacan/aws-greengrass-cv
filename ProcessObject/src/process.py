import sys
import traceback
import cv2
import os
from pyzbar import pyzbar
from datetime import datetime  

import boto3

import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    SubscriptionResponseMessage
)
# TO DO: Make this configurable
topic = 'devices/ObjectState'

session = boto3.Session()
s3 = session.resource('s3')
s3_client = boto3.client('s3')

class Process(client.SubscribeToTopicStreamHandler):
    def __init__(self, working_directory, dest_bucket, dest_folder, windows_mount):
        super().__init__()
        self.working_directory = working_directory
        self.dest_bucket = dest_bucket
        self.dest_folder = dest_folder
        self.windows_mount = windows_mount

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
            process_image(message["cameraId"], self.working_directory, self.dest_bucket, self.dest_folder, self.windows_mount)
        except:
            traceback.print_exc()

    def on_stream_error(self, error: Exception) -> bool:
        print('Received a stream error.', file=sys.stderr)
        traceback.print_exc()
        return False  # Return True to close stream, False to keep stream open.

    def on_stream_closed(self) -> None:
        print('Subscribe to topic stream closed.')

def process_image(camera_id, working_directory, dest_bucket, dest_folder, windows_mount):
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

        current_time = datetime.now()
        time_stamp = current_time.timestamp()

        date_time = datetime.fromtimestamp(time_stamp)

        str_date_time = date_time.strftime("%Y-%m-%d_%H.%M.%S")
        # Format: PL_XXXXXXXXXX_YYYY-MM-DD_HH.MI.SS.jpg
        save_filename = 'PL_{}_{}.jpg'.format(str(barcodeData), str_date_time)
        print("Saving file name: {}".format(save_filename))
        save_to_s3(working_directory, image_name, save_filename, dest_bucket, dest_folder)

        # Resize and upload
        resize_img = resize(img, 50)

        save_img_to_s3(resize_img, save_filename, dest_bucket, dest_folder + '/resize')

        save_to_folder(resize_img, save_filename, windows_mount)



def resize(img, scale_pct=50):
    print("Resizing image")

    width = int(img.shape[1] * scale_pct / 100)
    height = int(img.shape[0] * scale_pct / 100)
    dim = (width, height)
    
    # resize image
    return cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

def save_to_s3(working_directory, input_filename, output_filename, dest_bucket, dest_folder):
    print("Saving to s3")

    s3.Bucket(dest_bucket).upload_file(os.path.join(working_directory, input_filename), dest_folder + '/'+ output_filename )

def save_img_to_s3(input, output_filename, dest_bucket, dest_folder):
    print("Saving img to s3")

    image_string = cv2.imencode('.jpg', input)[1].tostring()

    s3_client.put_object(Bucket=dest_bucket, Key = dest_folder + '/'+ output_filename, Body=image_string)

def save_to_folder(input, output_filename, out_directory):
    print("Saving to folder")
    cv2.imwrite(os.path.join(out_directory, output_filename), input)

  