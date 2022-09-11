import argparse
import src.detector as detector
import time

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--working_directory", type=str, default="/tmp/video_tmp", help="Local directory for storing images.")

    return parser.parse_known_args()


def main():
    args, _ = parse_args()
    print("Arguments", args)

    test_detector = detector.detector(args.working_directory)

    while True:
        print("Running detector")
        test_detector.run()
        time.sleep(15)

if __name__ == "__main__":
    main()