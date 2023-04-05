# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import sys

# disable CUDA cache as it can throw errors when doing distributed
# training and the cache folder is on NFS
os.environ["CUDA_CACHE_DISABLE"] = "1"

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
game = os.path.join(root, "build/src")
if game not in sys.path:
    sys.path.append(game)
