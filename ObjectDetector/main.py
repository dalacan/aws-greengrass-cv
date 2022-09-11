import argparse
import src.detector as detector
import src.streamhandler as streamhandler
import time
import json
import sys
from awsiot.greengrasscoreipc.clientv2 import GreengrassCoreIPCClientV2
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    SubscribeToTopicRequest,
    UnauthorizedError
)
import traceback

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--working_directory", type=str, default="/tmp/video_tmp", help="Local directory for storing images.")
    parser.add_argument("-t", "--topic", type=str, default="devices/ObjectState", help="Object state topic.")
    return parser.parse_known_args()


def main():
    args, _ = parse_args()
    print("Arguments", args)

    test_detector = detector.detector(args.working_directory)

    object_state = {}

    try:
        ipc_client = GreengrassCoreIPCClientV2()
        handler = streamhandler.StreamHandler(object_state)
        _, operation = ipc_client.subscribe_to_topic(topic=args.topic, on_stream_event=handler.on_stream_event,
                                                     on_stream_error=handler.on_stream_error, on_stream_closed=handler.on_stream_closed)
        print('Successfully subscribed to topic: ' + args.topic)

        while True:
            print("Running detector")
            print("object_state")
            print(object_state)
            test_detector.run(handler.object_state)
            time.sleep(15)
        
        operation.close()

    except UnauthorizedError:
        print('Unauthorized error while subscribing to topic: ' +
              topic, file=sys.stderr)
        traceback.print_exc()
        exit(1)
    except Exception:
        print('Exception occurred', file=sys.stderr)
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main()