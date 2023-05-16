import json
import numpy as np

#this function sorts all the class results in the array as a sentence
def sort_letters(predict_json: json):
    
    #get the result values [x, y, width, height, confidence, class] then merge
    preds_x = []
    for result in predict_json:
        preds_x.append(result['x'])
    preds_y = []
    for result in predict_json:
        preds_y.append(result['y']) 
    preds_w = []
    for result in predict_json:
        preds_w.append(result['width']) 
    preds_h = []
    for result in predict_json:
        preds_h.append(result['height'])
    preds_class = []
    for result in predict_json:
        preds_class.append(result['class'])
    pred_shape = list(zip(preds_x, preds_y, preds_w, preds_h, preds_class)) 

    #sort y coordinate
    def sortY(val): return val[1]
    def sortX(val): return val[0]
    pred_shape.sort(key= sortY)

    #line break/space threshold
    arr = np.array(pred_shape, dtype=object)
 
    y_diff = np.array(preds_y)
    y_diff.sort()
    y_threshold = np.mean(preds_h, dtype = float) // 2
    boxes_y_diff = np.diff(y_diff)
    y_threshold_index = np.where(boxes_y_diff > y_threshold)[0]


    #check if img is sentence or paragraph
    if len(y_threshold_index) == 0:
        pred_shape.sort(key= sortX)
        arr = np.array(pred_shape, dtype=object)
        sorted_list = arr.tolist()
        labels = [x.pop(4) for x in sorted_list]
        final_result = ("".join(labels))
    else:
        # cluster/ split array according to threshold_index
        boxes_clustered = np.array_split(arr, y_threshold_index + 1)
        boxes_return = []
        count = -1
        x_diff = []
        for cluster in boxes_clustered:
            #sort x coordinate
            cluster = cluster[cluster[:, 0].argsort()]
            boxes_return.append(cluster)

            # get the x difference
            count += 1
            x = len(cluster)
            for a in range(x):
                x_diff.append(boxes_return[count][a][0])



        #--WORK IN PROGRESS--- (SPLITING SPACES)
        x_diff = np.array(x_diff, dtype = float)
        boxes_x_diff = np.diff(x_diff)
        x_threshold = np.mean(preds_w, dtype = float) // 2



        #iterate the labels through the 3d array
        labels = []
        for j in range(len(boxes_return)):
            labels.append(' ')
            for k in range(len(boxes_return[j])):
                count=0
                for l in range(len(boxes_return[j][k])):
                    count+=1
                    if count == 5:
                        labels.append(boxes_return[j][k][l])

        #output the string result
        final_result = ("".join(labels))
    return final_result