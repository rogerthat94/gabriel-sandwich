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

import cv2
import xml.etree.ElementTree as ET

class Task:
    def __init__(self):
        tree = ET.parse("recipe.xml")
        root = tree.getroot()
        instructions = root.find('instructions')
        self.instructions = {}
        for instruction in instructions:
            state = instruction.get('state')
            speech = instruction.find('speech').text.strip()
            image_path = instruction.find('image').get('path')
            image = cv2.imread(image_path) if image_path else None
            self.instructions[state] = {'speech' : speech, 'image' : image}

        self.current_state = "nothing"

    def update_state(self, state):
        self.current_state = state

    def get_instruction(self):
        return self.instructions[self.current_state]

    def get_current_state(self):
        return self.current_state

