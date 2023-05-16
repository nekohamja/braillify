import json
import numpy as np
import torch


def convert_to_braille_unicode(str_input: str, path: str = "braille_map.json") -> str:
    with open(path, "r", encoding='utf-8') as fl:
        data = json.load(fl)


    if str_input in data.keys():
        str_output = data[str_input]

        print(str_output)
    return str_output


def parse_xywh_and_class(boxes: torch.Tensor) -> list:

    # copy values from troublesome "boxes" object to numpy array
    new_boxes = np.zeros(boxes.shape)
    new_boxes[:, :4] = boxes.xywh.numpy()  # first 4 channels are xywh
    new_boxes[:, 4] = boxes.conf.numpy()  # 5th channel is confidence
    new_boxes[:, 5] = boxes.cls.numpy()  # 6th channel is class which is last channel

    # sort according to y coordinate
    new_boxes = new_boxes[new_boxes[:, 1].argsort()]

    # find threshold index to break the line
    y_threshold = np.mean(new_boxes[:, 3]) // 2
    boxes_diff = np.diff(new_boxes[:, 1])
    threshold_index = np.where(boxes_diff > y_threshold)[0]

    # cluster according to threshold_index
    boxes_clustered = np.split(new_boxes, threshold_index + 1)
    boxes_return = []
    for cluster in boxes_clustered:
        # sort according to x coordinate
        cluster = cluster[cluster[:, 0].argsort()]
        boxes_return.append(cluster)

    return boxes_return