import cv2
import threading
import os
import time

class video(threading.Thread):
    def __init__(self, camera_id, working_directory, interval):
        threading.Thread.__init__(self)
        self.camera_id = camera_id
        self.working_directory = working_directory
        self.interval = interval

    def run(self):
        while True:
            videoToFrame(self.camera_id, self.working_directory)
            time.sleep(self.interval)

def videoToFrame(camera_id, working_directory):
    cam = cv2.VideoCapture(camera_id)

    width = 1920
    height =1080
    cam.set(3, width)
    cam.set(4, height)

    print("Reading camera stream: ", camera_id)
    ret, image = cam.read()
    image_name = str(camera_id) + '.jpg'
    if ret:
        print("Writing to ", os.path.join(working_directory, image_name))
        cv2.imwrite(os.path.join(working_directory, image_name), image)

    # Release camera
    cam.release()
    cv2.destroyAllWindows()

