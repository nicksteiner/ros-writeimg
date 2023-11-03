import os
import sys
import argparse
import pathlib
import datetime

import cv2
import numpy as np
import rosbag
from bagpy import bagreader
import cv_bridge

data_class = {
    'path': '/lio_sam/mapping/path',
}

data_class_inv = {v: k for k, v in data_class.items()}

depth_dtype = {
    '16UC1': np.uint16
}
color_type = {
    'default': np.uint8
}

get_ts = lambda x: datetime.datetime.utcfromtimestamp(x.to_sec()).strftime('%Y-%m-%dT%H%M%St%f')


def setup_paths(bagfile_name):
    bag_file_path = pathlib.Path(bagfile_name)
    out_path = bag_file_path.parent / f'path_{bag_file_path.stem}'
    out_path.mkdir(exist_ok=True)
    return out_path

def main():
    
    project = pathlib.Path(args.filename).parent.absolute().name
    out_path = setup_paths(args.filename)
    # setup vars
    #initialize csv file
    with open(out_path / f'path_{pathlib.Path(args.filename).stem}.csv', 'w') as f:
        with rosbag.Bag(args.filename, 'r') as bag:
            for topic, msg, t in bag.read_messages(topics=list(data_class.values())):
                print(topic, t)
                if data_class_inv[topic] == 'path':
                    record_ = {
                        'timestamp': msg.header.stamp.to_sec(),
                        'x': msg.pose.position.x,
                        'y': msg.pose.position.y,
                        'z': msg.pose.position.z,
                        'qx': msg.pose.orientation.x,
                        'qy': msg.pose.orientation.y,
                        'qz': msg.pose.orientation.z,
                        'qw': msg.pose.orientation.w,
                    }
                    f.write(','.join([str(record_[k]) for k in record_.keys()]) + '\n')
                    f.flush()
                    os.fsync(f.fileno())
                    print(record_)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='filename',  default='/home/nsteiner/2023-10-02-22-58-04.bag')
    args = parser.parse_args()
    main()
