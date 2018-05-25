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

import caffe
import cv2
import numpy as np
import os
import sys
import time

sys.path.insert(0, "..")
import config
import zhuocv as zc

current_milli_time = lambda: int(round(time.time() * 1000))


# Caffe configuration and preparation
caffe_root = os.getenv('CAFFE_ROOT', '.')
caffe.set_mode_gpu()
net = caffe.Net(os.path.join(caffe_root, 'models/toy_sandwich/deploy.prototxt'),
                os.path.join(caffe_root, 'models/toy_sandwich/toy_sandwich.caffemodel'),
                caffe.TEST)

# input preprocessing: 'data' is the name of the input blob == net.inputs[0]
transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
transformer.set_transpose('data', (2,0,1))
transformer.set_mean('data', np.load(os.path.join(caffe_root, 'python/caffe/imagenet/ilsvrc_2012_mean.npy')).mean(1).mean(1)) # mean pixel

#############################################################
def set_config(is_streaming):
    config.setup(is_streaming)

def process(img, display_list):
    ## the detection
    caffe.set_mode_gpu()
    rect_detected, label_idxes_detected = zc.object_detection(img, config.LABELS, net = net, transformer = transformer)

    ## display raw detections (bounding boxes may overlap a lot)
    if 'raw' in display_list or 'object' in display_list:
        img_display = img.copy()
    if 'raw' in display_list:
        for idx, rect in enumerate(rect_detected):
            x1, y1, x2, y2 = rect
            #print("rect: top %d, bottom %d, left %d, right %d; label: %s" % (y1, y2, x1, x2, config.LABELS[label_idxes_detected[idx]]))
            cv2.rectangle(img_display, (x1, y1), (x2, y2), (0, 0, 255), 1)

    ## non-maximum suppression
    rect_suppressed, pick = zc.non_max_suppression_fast(np.array(rect_detected), 0.35)
    label_idxes_suppress = np.array(label_idxes_detected)[pick]
    if 'object' in display_list:
        for idx, rect in enumerate(rect_suppressed):
            x1, y1, x2, y2 = rect
            #print("rect: top %d, bottom %d, left %d, right %d; label: %s" % (y1, y2, x1, x2, config.LABELS[label_idxes_suppress[idx]]))
            cv2.rectangle(img_display, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img_display, config.LABELS[label_idxes_suppress[idx]], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, [0, 255, 0])
        zc.check_and_display('object', img_display, display_list, resize_max = config.DISPLAY_MAX_PIXEL, wait_time = config.DISPLAY_WAIT_TIME)

    ## see if multiple objects are detected
    state_idx = None
    for label_idx in label_idxes_suppress:
        if not state_idx:
            state_idx = label_idx
            continue
        if label_idx != state_idx:
            state_idx = None
            break

    # convert state index to state (string)
    state = None
    if state_idx is not None:
        state = config.LABELS[state_idx]

    rtn_msg = {'status' : 'success'}
    return (rtn_msg, state)
