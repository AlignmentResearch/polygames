# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import datetime
import os
import sys


class Logger:
    def __init__(self, path, mode="w"):
        assert mode in {"w", "a"}, "unknown mode for logger %s" % mode
        self.terminal = sys.stdout
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        if mode == "w" or not os.path.exists(path):
            self.log = open(path, "w")
        else:
            self.log = open(path, "a")

    def write(self, message):
        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
        message_with_timestamp = timestamp + message

        self.terminal.write(message_with_timestamp)
        self.log.write(message_with_timestamp)
        self.log.flush()

    def flush(self):
        # for python 3 compatibility.
        pass
