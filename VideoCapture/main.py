import sys
import argparse
import src.video as video
import cv2
import os
import time

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interval", type=int, default=30, help="Camera capture intervals")
    parser.add_argument("-d", "--working_directory", type=str, default="/tmp/video_tmp", help="Local directory for storing images.")

    return parser.parse_known_args()

def main():
    args, _ = parse_args()
    print("Arguments", args)

    # Check working directory
    if not os.path.isdir(args.working_directory):
        print("Creating working directory")
        os.mkdir(args.working_directory)

    # Get a list of cameras
    print("Scanning for cameras")
    connected_cam = []
    for port in range(0, 10):
        print("Attempting to open camera on port {}".format(port))
        try:
            cam = cv2.VideoCapture(port)
            time.sleep(0.1)
            if cam.isOpened():
                print("Camera found")
                connected_cam.append(port)
            cam.release()
            cv2.destroyAllWindows()
        except:
            cam.release()
            cv2.destroyAllWindows()
    
    print("Found {} cameras".format(len(connected_cam)))
    threads = []
    for idx, camera_id in enumerate(connected_cam):
        print("Start streaming for camera: {}".format(camera_id))
        threads.append(video.video(camera_id, args.working_directory, args.interval))
        threads[idx].start()

if __name__ == "__main__":
    main()