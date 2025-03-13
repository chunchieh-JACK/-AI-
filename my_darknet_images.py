import os
import glob
import random
import darknet
import time
import cv2
import numpy as np
import darknet

alt_parser = {  "input" : "",
          "batch_size" : 1,  
          "weights" : "",
          "config_file" : "",
          "data_file" : "",
          "thresh" : .25
        }


def check_arguments_errors(alt_parser):
    assert 0 < alt_parser["thresh"] < 1, "Threshold should be a float between zero and one (non-inclusive)"
    if not os.path.exists(alt_parser["config_file"]):
        raise(ValueError("Invalid config path {}".format(os.path.abspath(alt_parser["config_file"]))))
    if not os.path.exists(alt_parser["weights"]):
        raise(ValueError("Invalid weight path {}".format(os.path.abspath(alt_parser["weights"]))))
    if not os.path.exists(alt_parser["data_file"]):
        raise(ValueError("Invalid data file path {}".format(os.path.abspath(alt_parser["data_file"]))))
    #if alt_parser["input"] and not os.path.exists(alt_parser["input"]):
    #    raise(ValueError("Invalid image path {}".format(os.path.abspath(alt_parser["input"]))))


def check_batch_shape(images, batch_size):
    """
        Image sizes should be the same width and height
    """
    shapes = [image.shape for image in images]
    if len(set(shapes)) > 1:
        raise ValueError("Images don't have same shape")
    if len(shapes) > batch_size:
        raise ValueError("Batch size higher than number of images")
    return shapes[0]


def load_images(images_path):
    """
    If image path is given, return it directly
    For txt file, read it and return each line as image path
    In other case, it's a folder, return a list with names of each
    jpg, jpeg and png file
    """
    input_path_extension = images_path.split('.')[-1]
    if input_path_extension in ['jpg', 'jpeg', 'png']:
        return [images_path]
    elif input_path_extension == "txt":
        with open(images_path, "r") as f:
            return f.read().splitlines()
    else:
        return glob.glob(
            os.path.join(images_path, "*.jpg")) + \
            glob.glob(os.path.join(images_path, "*.png")) + \
            glob.glob(os.path.join(images_path, "*.jpeg"))


def prepare_batch(images, network, channels=3):
    width = darknet.network_width(network)
    height = darknet.network_height(network)

    darknet_images = []
    for image in images:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_resized = cv2.resize(image_rgb, (width, height),
                                   interpolation=cv2.INTER_LINEAR)
        custom_image = image_resized.transpose(2, 0, 1)
        darknet_images.append(custom_image)

    batch_array = np.concatenate(darknet_images, axis=0)
    batch_array = np.ascontiguousarray(batch_array.flat, dtype=np.float32)/255.0
    darknet_images = batch_array.ctypes.data_as(darknet.POINTER(darknet.c_float))
    return darknet.IMAGE(width, height, channels, darknet_images)



def image_detection(image_path, network, class_names, class_colors, thresh):
    # Darknet doesn't accept numpy images.
    # Create one with image we reuse for each detect
    width = darknet.network_width(network)
    height = darknet.network_height(network)
    darknet_image = darknet.make_image(width, height, 3)

    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image_rgb, (width, height),
                               interpolation=cv2.INTER_LINEAR)

    darknet.copy_image_from_bytes(darknet_image, image_resized.tobytes())
    detections = darknet.detect_image(network, class_names, darknet_image, thresh=thresh)
    darknet.free_image(darknet_image)
    image = darknet.draw_boxes(detections, image_resized, class_colors)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB), detections
    #cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def batch_detection(network, images, class_names, class_colors,
                    thresh=0.25, hier_thresh=.5, nms=.45, batch_size=4):
    image_height, image_width, _ = check_batch_shape(images, batch_size)
    darknet_images = prepare_batch(images, network)
    batch_detections = darknet.network_predict_batch(network, darknet_images, batch_size, image_width,
                                                     image_height, thresh, hier_thresh, None, 0, 0)
    batch_predictions = []
    for idx in range(batch_size):
        num = batch_detections[idx].num
        detections = batch_detections[idx].dets
        if nms:
            darknet.do_nms_obj(detections, num, len(class_names), nms)
        predictions = darknet.remove_negatives(detections, class_names, num)
        images[idx] = darknet.draw_boxes(predictions, images[idx], class_colors)
        batch_predictions.append(predictions)
    darknet.free_batch_detections(batch_detections, batch_size)
    return images, batch_predictions


def image_classification(image, network, class_names):
    width = darknet.network_width(network)
    height = darknet.network_height(network)
    image = cv2.imread(image)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image_rgb, (width, height),
                                interpolation=cv2.INTER_LINEAR)
    darknet_image = darknet.make_image(width, height, 3)
    darknet.copy_image_from_bytes(darknet_image, image_resized.tobytes())
    detections = darknet.predict_image(network, darknet_image)
    predictions = [(name, detections[idx]) for idx, name in enumerate(class_names)]
    darknet.free_image(darknet_image)
    return sorted(predictions, key=lambda x: -x[1])


def convert2relative(image, bbox):
    """
    YOLO format use relative coordinates for annotation
    """
    x, y, w, h = bbox
    height, width, _ = image.shape
    return x/width, y/height, w/width, h/height


def save_annotations(name, image, detections, class_names):
    """
    Files saved with image_name.txt and relative coordinates
    """
    file_name = os.path.splitext(name)[0] + ".txt"
    with open(file_name, "w") as f:
        for label, confidence, bbox in detections:
            x, y, w, h = convert2relative(image, bbox)
            label = class_names.index(label)
            f.write("{} {:.4f} {:.4f} {:.4f} {:.4f} {:.4f}\n".format(label, x, y, w, h, float(confidence)))

def load_model(cfg,data,weights):
    alt_parser["config_file"] = cfg
    alt_parser["data_file"] = data
    alt_parser["weights"] = weights
    check_arguments_errors(alt_parser)
    network, class_names, class_colors = darknet.load_network(
    alt_parser["config_file"],
    alt_parser["data_file"],
    alt_parser["weights"],
    alt_parser["batch_size"]
    )
    return (network, class_names, class_colors)

def main():
    #args = parser()
    #check_arguments_errors(args)

    random.seed(3)  # deterministic bbox colors
    network, class_names, class_colors = darknet.load_network(
        alt_parser["config_file"],
        alt_parser["data_file"],
        alt_parser["weights"],
        batch_size=alt_parser["batch_size"]
    )

    images = load_images(alt_parser["input"])

    index = 0
    while True:
        # loop asking for new image paths if no list is given
        if alt_parser["input"]:
            if index >= len(images):
                break
            image_name = images[index]
        else:
            image_name = input("Enter Image Path: ")
        prev_time = time.time()
        image, detections = image_detection(
            image_name, network, class_names, class_colors, alt_parser["thresh"]
            )
        if alt_parser["save_labels"]:
            save_annotations(image_name, image, detections, class_names)
        #darknet.print_detections(detections, args.ext_output)
        fps = int(1/(time.time() - prev_time))
        print("FPS: {}".format(fps))

        index += 1


if __name__ == "__main__":
    # unconmment next line for an example of batch processing
    # batch_detection_example()
    main()
