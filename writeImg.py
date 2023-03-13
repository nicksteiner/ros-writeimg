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
    'depth': '/camera/aligned_depth_to_color/image_raw',
    'color': '/camera/color/image_rect_color/compressed'
}
data_class_inv = {v: k for k, v >

def main():
    #b = bagreader(args.filename)
    #print(b.topic_table)

    project = pathlib.Path(args.filename).parent.absolute().name
    out_path = setup_paths(args.filename)
    # setup vars
    pair_count = 0
    do_write_depth = False
    message_queue = {'depth': None, 'color': None}

    with rosbag.Bag(args.filename, 'r') as bag:
        for topic, msg, t in bag.read_messages(topics=list(data_class.values())):
            print(topic, t)
            if data_class_inv[topic] == 'color':
                if do_write_depth:
                    if message_queue['color'] is not None:
                        old_msg, old_time  = message_queue['color']
                        depth_msg, depth_time = message_queue['depth']
                        if (depth_time - old_time) > (t - depth_time):
                            color_msg = msg
                            color_time = t
                        else:
                            color_msg = old_msg
                            color_time = old_time
                    else:
                        color_msg = msg
                        color_time = t
                    # write depth image
                    write_images(color_msg, color_time, depth_msg, depth_time, project, pair_count, out_path)
                    pair_count += 1
                    do_write_depth = False
                else:
                    message_queue['color'] = (msg, t)
            if data_class_inv[topic] == 'depth':
                message_queue['depth'] = (msg, t)
                do_write_depth = True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='filename',  default='test_bag.bag')
    args = parser.parse_args()
    main()