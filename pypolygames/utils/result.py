# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# helper class for result stats


def parse_reward(reward):
    result = {"win": 0, "loss": 0, "tie": 0, "avg": 0.0}
    for r in reward:
        if r == -1:
            result["loss"] += 1
        elif r == 1:
            result["win"] += 1
        else:
            result["tie"] += 1
    result["total"] = len(reward)
    result["avg"] = (sum(reward) / max(len(reward), 1) + 1.0) / 2.0
    return result


class Result:
    def __init__(self, reward):
        self.reward = reward
        self.result = parse_reward(reward)

    def log(self):
        total = max(self.result["total"], 1)
        s = "win: %.2f, tie: %.2f, loss: %.2f, avg: %.2f" % (
            100 * self.result["win"] / total,
            100 * self.result["tie"] / total,
            100 * self.result["loss"] / total,
            100 * self.result["avg"],
        )
        return s
