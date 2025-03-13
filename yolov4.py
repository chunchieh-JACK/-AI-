from flask import Flask, request, jsonify
import my_darknet_images as dk
import cv2

def yolo_detect(im=None,
                img_path=None,
                data='train/cfg/obj.data',
                cfg='train/cfg/yolov4-tiny-obj.cfg',
                weights='train/cfg/weights/yolov4-tiny-obj_final.weights',
                ):
 
    if img_path == None:
        img = im
    else:
        img = cv2.imread(img_path)

    (network, class_names, class_colors)= dk.load_model(cfg,data,weights)
    img2, prediction = dk.image_detection(img_path, network, class_names, class_colors, 0.25)
    print(prediction)

    return prediction,img2