#!/usr/bin/env python
import os
import cv2
import dlib
import glob
import time
import caffe
import skimage
import argparse
import numpy as np

LABELS = ["bread", "ham", "cucumber", "lettuce", "cheese", "half", "hamwrong", "tomato", "full", "nothing"]

## Caffe configuration and preparation
caffe_root = os.getenv('CAFFE_ROOT', '.')
caffe.set_mode_cpu()
net = caffe.Net(os.path.join(caffe_root, 'models/toy_sandwich/deploy.prototxt'),
                os.path.join(caffe_root, 'models/toy_sandwich/toy_sandwich.caffemodel'),
                caffe.TEST)

# input preprocessing: 'data' is the name of the input blob == net.inputs[0]
transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
transformer.set_transpose('data', (2,0,1))
transformer.set_mean('data', np.load(os.path.join(caffe_root, 'python/caffe/imagenet/ilsvrc_2012_mean.npy')).mean(1).mean(1)) # mean pixel
transformer.set_raw_scale('data', 255)  # the reference model operates on images in [0,255] range instead of [0,1]
# the reference model has channels in BGR order instead of RGB
# a good reference: https://github.com/BVLC/caffe/issues/2598
transformer.set_channel_swap('data', (2,1,0))


### http://www.pyimagesearch.com/2015/02/16/faster-non-maximum-suppression-python/
def non_max_suppression_fast(boxes, overlapThresh):
    if len(boxes) == 0:
        return []

    # if the bounding boxes are integers, convert them to floats --
    # this is important since we'll be doing a bunch of divisions
    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")

    # initialize the list of picked indexes
    pick = []

    # grab the coordinates of the bounding boxes
    x1 = boxes[:,0]
    y1 = boxes[:,1]
    x2 = boxes[:,2]
    y2 = boxes[:,3]

    # compute the area of the bounding boxes and sort the bounding
    # boxes by the bottom-right y-coordinate of the bounding box
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(y2)

    # keep looping while some indexes still remain in the indexes list
    while len(idxs) > 0:
        # grab the last index in the indexes list and add the
        # index value to the list of picked indexes
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        # find the largest (x, y) coordinates for the start of
        # the bounding box and the smallest (x, y) coordinates
        # for the end of the bounding box
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        # compute the ratio of overlap
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        overlap = (w * h) / area[idxs[:last]]

        # delete all indexes from the index list that overlap too much
        idxs = np.delete(idxs, np.concatenate(([last],
            np.where(overlap > overlapThresh)[0])))

    return boxes[pick].astype("int"), pick

def test_image(img_path):
    ## selective search to find candidate bounding boxes
    sk_img = skimage.io.imread(img_path)
    cv_img = cv2.imread(img_path)
    caffe_img = caffe.io.load_image(img_path)
    rects = [] # locations of the candidates
    dlib.find_candidate_object_locations(sk_img, rects, min_size = 2500)

    ## count how many rects are promissing
    rect_candidates = []
    for rect in rects:
        x1, y1, x2, y2 = rect.left(), rect.top(), rect.right(), rect.bottom()
        aspect_ratio = float(y2 - y1) / (x2 - x1)
        if aspect_ratio > 0.6 and aspect_ratio < 1.6 \
                and y1 != 0 and y2 != sk_img.shape[0] - 1 and x1 != 0 and x2 != sk_img.shape[1] - 1:
            rect_candidates.append([x1, y1, x2, y2])
    data_layer = net.blobs['data']
    data_layer.reshape(len(rect_candidates), data_layer.channels, data_layer.height, data_layer.width)

    ## do recognition for the rects in a batch
    for idx, rect in enumerate(rect_candidates):
        x1, y1, x2, y2 = rect
        img_rect = caffe_img[y1 : y2 + 1, x1 : x2 + 1, :]
        net.blobs['data'].data[idx, ...] = transformer.preprocess('data', img_rect)

    ## real DNN processing
    out = net.forward()
    label_idxes = out['prob'].argmax(axis = 1)

    ## find rects that are not just background
    rect_detected = []
    label_idxes_detected = []
    for idx, rect in enumerate(rect_candidates):
        if label_idxes[idx] != len(LABELS) - 1:
            rect_detected.append(rect)
            label_idxes_detected.append(label_idxes[idx])

    ## display raw detections (bounding boxes may overlap a lot)
    img_display = cv_img.copy()
    for idx, rect in enumerate(rect_detected):
        x1, y1, x2, y2 = rect
        #print("rect: top %d, bottom %d, left %d, right %d; label: %s" % (y1, y2, x1, x2, LABELS[label_idxes_detected[idx]]))
        cv2.rectangle(img_display, (x1, y1), (x2, y2), (0, 0, 255), 1)

    ## non-maximum suppression
    rect_suppressed, pick = non_max_suppression_fast(np.array(rect_detected), 0.35)
    label_idxes_suppress = np.array(label_idxes_detected)[pick]
    for idx, rect in enumerate(rect_suppressed):
        x1, y1, x2, y2 = rect
        #print("rect: top %d, bottom %d, left %d, right %d; label: %s" % (y1, y2, x1, x2, LABELS[label_idxes_suppress[idx]]))
        cv2.rectangle(img_display, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img_display, LABELS[label_idxes_suppress[idx]], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, [0, 255, 0])

    cv2.imshow('object detection',img_display)
    cv2.waitKey()

def main():
    test_path = parse_arguments()
    if os.path.isfile(test_path):
        test_image(test_path)
    elif os.path.isdir(test_path):
        for img_path in sorted(glob.glob(os.path.join(test_path, '*'))):
            print "now testing image at: %s" % img_path
            test_image(img_path)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("test_path",
                        help = "Test image or folder of images",
                        )
    args = parser.parse_args()

    return (args.test_path)

if __name__ == "__main__":
    main()
