import json
import numpy as np

#this function sorts all the class results in the array as a sentence
def sort_letters(predict_json: json):
    
    #get the result values [x, y, width, height, confidence, class]
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

    #merge
    pred_shape = list(zip(preds_x, preds_y, preds_w, preds_h, preds_class)) 

    #sort by y then x
    def sortY(val): return val[1]
    def sortX(val): return val[0]
    pred_shape.sort(key= sortY)
    pred_shape.sort(key= sortX)
    arr = np.array(pred_shape)

    #---------WORK IN PROGRESS---------
    #manually get the difference

    #find threshold to break the line  / mean: avg / y value increases the more letters go down
    #y_threshold = np.mean(arr[:, 1], dtype = 'float') // 2
    #boxes_diff = np.diff(np.append(arr[:, 1], arr))
    
    #test
    #print(arr)
    #print('-----x-------y---width---height---label')
    #print(y_threshold)

    sorted_list = arr.tolist()

    #output the string result
    squeeze = [x.pop(4) for x in sorted_list]
    final_result = ("".join(squeeze))
    return final_result
