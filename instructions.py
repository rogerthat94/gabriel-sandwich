# Cloudlet Infrastructure for Mobile Computing
#   - Task Assistance
#
#   Author: Zhuo Chen <zhuoc@cs.cmu.edu>
#           Roger Iyengar <iyengar@cmu.edu>
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

import math
import instruction_pb2
from gabriel_protocol import gabriel_pb2
from collections import namedtuple

ENGINE_NAME = "instruction"

LABELS = ["bread", "ham", "cucumber", "lettuce", "cheese", "half", "hamwrong",
          "tomato", "full"]

Hologram = namedtuple('Hologram', ['dist', 'x', 'y', 'label_index'])

HAM_HOLO = Hologram(dist=6500, x=0.5, y=0.36, label_index=0)
LETTUCE_HOLO = Hologram(dist=6800, x=0.5, y=0.32, label_index=1)
BREAD_HOLO = Hologram(dist=7100, x=0.5, y=0.3, label_index=3)
TOMATO_HOLO = Hologram(dist=7500, x=0.5, y=0.26, label_index=5)
BREAD_TOP_HOLO = Hologram(dist=7800, x=0.5, y=0.22, label_index=7)


def _update_holo_location(objects, holo, engine_fields):
    # This modifies engine fields
    # TODO: Make this a method of an object that contains engine_fields as a
    #       member
    objects = objects[objects[:, -1] == holo.label_index, :]
    x1, y1, x2, y2 = objects[0, :4]
    x = x1 * (1 - holo.x) + x2 * holo.x
    y = y1 * (1 - holo.y) + y2 * holo.y
    area = (y2 - y1) * (x2 - x1)

    depth = math.sqrt(holo.dist / float(area))
    engine_fields.sandwich.holo_x = x
    engine_fields.sandwich.holo_y = y
    engine_fields.sandwich.holo_depth = depth


def _result_with_update(
        image_path, instruction, engine_fields):
    engine_fields.update_count += 1

    result_wrapper = _result_without_update(engine_fields)

    result = gabriel_pb2.ResultWrapper.Result()
    result.payload_type = gabriel_pb2.PayloadType.IMAGE
    result.engine_name = ENGINE_NAME
    with open(image_path, 'rb') as f:
        result.payload = f.read()
    result_wrapper.results.append(result)

    result = gabriel_pb2.ResultWrapper.Result()
    result.payload_type = gabriel_pb2.PayloadType.TEXT
    result.engine_name = ENGINE_NAME
    result.payload = instruction.encode(encoding="utf-8")
    result_wrapper.results.append(result)

    return result_wrapper


def _result_without_update(engine_fields):
    result_wrapper = gabriel_pb2.ResultWrapper()
    result_wrapper.engine_fields.Pack(engine_fields)
    return result_wrapper


def _start_result(engine_fields):
    engine_fields.sandwich.state = instruction_pb2.Sandwich.State.NOTHING
    return _result_with_update(
        "images_feedback/bread.jpeg", "Now put a piece of bread on the table.",
        engine_fields)


def _nothing_result(objects, object_counts, engine_fields):
    if object_counts[0] == 0:
        return _result_without_update(engine_fields)

    engine_fields.sandwich.state = instruction_pb2.Sandwich.State.BREAD
    _update_holo_location(objects, HAM_HOLO, engine_fields)
    return _result_with_update(
        "images_feedback/ham.jpeg", "Now put a piece of ham on the bread.",
        engine_fields)


def _bread_result(objects, object_counts, engine_fields):
    if object_counts[1] == 0:
        if object_counts[0] > 0:
            engine_fields.update_count += 1
            _update_holo_location(objects, HAM_HOLO, engine_fields)
        return _result_without_update(engine_fields)

    engine_fields.sandwich.state = instruction_pb2.Sandwich.State.HAM
    _update_holo_location(objects, LETTUCE_HOLO, engine_fields)
    return _result_with_update(
        "images_feedback/lettuce.jpeg", "Now put a piece of lettuce on the "
        "ham.", engine_fields)


def _lettuce_helper(objects, engine_fields):
    engine_fields.sandwich.state = instruction_pb2.Sandwich.State.LETTUCE
    _update_holo_location(objects, BREAD_HOLO, engine_fields)
    return _result_with_update(
        "images_feedback/half.jpeg", "Now put a piece of bread on the lettuce.",
        engine_fields)


def _ham_result(objects, object_counts, engine_fields):
    if object_counts[3] > 0:
        return _lettuce_helper(objects, engine_fields)
    elif object_counts[2] > 0:
        engine_fields.sandwich.state = instruction_pb2.Sandwich.State.CUCUMBER
        return _result_with_update(
            "images_feedback/lettuce.jpeg", "This sandwich doesn't contain "
            "any cucumber. Replace the cucumber with lettuce.", engine_fields)
    elif object_counts[0] > 0 and object_counts[1] == 0:
        return _nothing_result(objects, object_counts, engine_fields)

    if object_counts[1] > 0:
        engine_fields.update_count += 1
        _update_holo_location(objects, LETTUCE_HOLO, engine_fields)
    return _result_without_update(engine_fields)


def _half_helper(objects, engine_fields):
    engine_fields.sandwich.state = instruction_pb2.Sandwich.State.HALF
    _update_holo_location(objects, TOMATO_HOLO, engine_fields)
    return _result_with_update(
        "images_feedback/tomato.jpeg", "You are half done. Now put a piece of "
        "tomato on the bread.", engine_fields)


def _lettuce_result(objects, object_counts, engine_fields):
    if object_counts[5] > 0:
        return _half_helper(objects, engine_fields)
    elif object_counts[1] > 0 and object_counts[3] == 0:
        return _bread_result(objects, object_counts, engine_fields)

    if object_counts[3] > 0:
        _update_holo_location(objects, BREAD_HOLO, engine_fields)
    return _result_without_update(engine_fields)


def _cucumber_result(objects, object_counts, engine_fields):
    if object_counts[3] > 0:
        return _lettuce_helper(objects, engine_fields)
    elif object_counts[1] > 0 and object_counts[3] == 0:
        return _bread_result(objects, object_counts, engine_fields)

    return _result_without_update(engine_fields)


def _tomato_helper(objects, engine_fields):
    engine_fields.sandwich.state = instruction_pb2.Sandwich.State.TOMATO
    _update_holo_location(objects, BREAD_TOP_HOLO, engine_fields)
    return _result_with_update(
        "images_feedback/full.jpeg", "Now put the bread on top and you will be "
        "done.", engine_fields)


def _half_result(objects, object_counts, engine_fields):
    if object_counts[7] > 0:
        return _tomato_helper(objects, engine_fields)
    elif object_counts[6] > 0:
        engine_fields.sandwich.state = instruction_pb2.Sandwich.State.HAM_WRONG
        return _result_with_update(
            "images_feedback/tomato.jpeg", "That's too much meat. Replace the "
            "ham with tomatoes.", engine_fields)
    elif object_counts[3] > 0 and object_counts[5] == 0:
        return _lettuce_helper(objects, engine_fields)

    if object_counts[5] > 0:
        engine_fields.update_count += 1
        _update_holo_location(objects, TOMATO_HOLO, engine_fields)
    return _result_without_update(engine_fields)


def _tomato_result(objects, object_counts, engine_fields):
    if object_counts[8] > 0:
        engine_fields.sandwich.state = instruction_pb2.Sandwich.State.FULL
        return _result_with_update(
            "images_feedback/full.jpeg", "Congratulations! You have made a "
            "sandwich!", engine_fields)
    elif object_counts[5] > 0 and object_counts[7] == 0:
        return _half_helper(objects, engine_fields)

    if object_counts[7] > 0:
        engine_fields.update_count += 1
        _update_holo_location(objects, BREAD_TOP_HOLO, engine_fields)
    return _result_without_update(engine_fields)


def _ham_wrong_result(objects, object_counts, engine_fields):
    if object_counts[7] > 0:
        return _tomato_helper(objects, engine_fields)
    elif object_counts[5] > 0:
        return _half_helper(objects, engine_fields)

    return _result_without_update(engine_fields)


def get_instruction(engine_fields, objects):
    state = engine_fields.sandwich.state

    if state == instruction_pb2.Sandwich.State.START:
        return _start_result(engine_fields)

    if len(objects.shape) < 2:
        return _result_without_update(engine_fields)

    # get the count of detected objects
    object_counts = [sum(objects[:, -1] == i) for i in range(len(LABELS))]

    if state == instruction_pb2.Sandwich.State.NOTHING:
        return _nothing_result(objects, object_counts, engine_fields)
    elif state == instruction_pb2.Sandwich.State.BREAD:
        return _bread_result(objects, object_counts, engine_fields)
    elif state == instruction_pb2.Sandwich.State.HAM:
        return _ham_result(objects, object_counts, engine_fields)
    elif state == instruction_pb2.Sandwich.State.LETTUCE:
        return _lettuce_result(objects, object_counts, engine_fields)
    elif state == instruction_pb2.Sandwich.State.CUCUMBER:
        return _cucumber_result(objects, object_counts, engine_fields)
    elif state == instruction_pb2.Sandwich.State.HALF:
        return _half_result(objects, object_counts, engine_fields)
    elif state == instruction_pb2.Sandwich.State.TOMATO:
        return _tomato_result(objects, object_counts, engine_fields)
    elif state == instruction_pb2.Sandwich.State.HAM_WRONG:
        return _ham_wrong_result(objects, object_counts, engine_fields)
    elif state == instruction_pb2.Sandwich.State.FULL:
        return _result_without_update(engine_fields)

    raise Exception("Invalid state")
