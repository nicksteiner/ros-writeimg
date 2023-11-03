import os
import sys
import argparse
import pathlib
import datetime

import cv2
import numpy as np
import rosbag
#from bagpy import bagreader
import cv_bridge

data_class = {
    'depth': '/camera/aligned_depth_to_color/image_raw',
    'color': '/camera/color/image_rect_color/compressed'
}
data_class_inv = {v: k for k, v in data_class.items()}

depth_dtype = {
    '16UC1': np.uint16
}
color_type = {
    'default': np.uint8
}

get_ts = lambda x: datetime.datetime.utcfromtimestamp(x.to_sec()).strftime('%Y-%m-%dT%H%M%St%f')

depth_range_mm = (0, 60000)
def write_images(color_msg, color_time, depth_msg, depth_time, project, pair_count, out_path):
    print(f'Writing pair ... {pair_count:06d}')
    color_file = f'{project}_{pair_count:06d}_color_{get_ts(color_time)}.png'
    depth_file = f'{project}_{pair_count:06d}_depth_{get_ts(depth_time)}.tif'

    d_dtype = np.dtype(depth_dtype[depth_msg.encoding])
    d_dtype = d_dtype.newbyteorder('>' if depth_msg.is_bigendian else '<')
    depth_arr = np.frombuffer(depth_msg.data, d_dtype).reshape((depth_msg.height, depth_msg.width))
    #depth_arr_norm = np.round(255 * ((depth_arr - depth_range_mm[0]) / (depth_range_mm[1] - depth_range_mm[0]))).astype('uint8')
    #depth_arr_norm[depth_arr > depth_range_mm[1]] = 255
    cv2.imwrite((out_path / depth_file).as_posix(), depth_arr)

    c_dtype = color_type['default']
    cv2.imwrite((out_path / color_file).as_posix(), cv2.imdecode(np.frombuffer(color_msg.data, c_dtype), cv2.IMREAD_COLOR))


def setup_paths(bagfile_name):
    bag_file_path = pathlib.Path(bagfile_name)
    out_path = bag_file_path.parent / 'img'
    out_path.mkdir(exist_ok=True)
    return out_path

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
