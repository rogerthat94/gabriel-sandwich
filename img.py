#!/usr/bin/env python
#
# Cloudlet Infrastructure for Mobile Computing
#   - Task Assistance
#
#   Author: Zhuo Chen <zhuoc@cs.cmu.edu>
#
#   Copyright (C) 2011-2013 Carnegie Mellon University
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# This script is used for testing computer vision algorithms in the
# Lego Task Assistance project. It does processing for one image.
# Usage: python img.py <image-path>
#

'''
This script loads a single image from file, and try to generate relevant information of Cooking Assistant.
It is primarily used as a quick test tool for the computer vision algorithm.
'''

import argparse
import cv2
import sys
import time

import config
import cooking_cv as cc
import zhuocv as zc

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file",
                        help = "The image to process",
                       )
    args = parser.parse_args()
    return (args.input_file)

# set configs...
config.setup(is_streaming = False)

# load test image
input_file = parse_arguments()
img = cv2.imread(input_file)
resize_ratio = 1
if max(img.shape) > config.IMAGE_MAX_WH:
    resize_ratio = float(config.IMAGE_MAX_WH) / max(img.shape[0], img.shape[1])
    img = cv2.resize(img, (0, 0), fx = resize_ratio, fy = resize_ratio, interpolation = cv2.INTER_AREA)

# process image and get the symbolic representation
rtn_msg, state = cc.process(img, resize_ratio=resize_ratio, display_list=[])
# the object detection result format is, for each line: [x1, y1, x2, y2, confidence, cls_idx]
# cls_idx corresponds to config.LABELS
print "Detection status: {}; detection results: {}".format(rtn_msg, state)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt as e:
    sys.stdout.write("user exits\n")
