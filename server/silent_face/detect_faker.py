import os
import cv2
import numpy as np
import argparse
import warnings

from silent_face.src.anti_spoof_predict import AntiSpoofPredict
from silent_face.src.generate_patches import CropImage
from silent_face.src.utility import parse_model_name
warnings.filterwarnings('ignore')


def check_image(image):
    height, width, channel = image.shape
    if width/height != 3/4:
        print("Image is not appropriate!!!\nHeight/Width should be 4/3.")
        return False
    else:
        return True


def detect_faker(image, model_dir = "silent_face/resources/anti_spoof_models", device_id = 0):
    model_test = AntiSpoofPredict(device_id)
    image_cropper = CropImage()
    result = check_image(image)
    if result is False:
        return
    image_bbox = model_test.get_bbox(image)
    prediction = np.zeros((1, 3))

    # sum the prediction from single model's result
    for model_name in os.listdir(model_dir):
        h_input, w_input, model_type, scale = parse_model_name(model_name)
        param = {
            "org_img": image,
            "bbox": image_bbox,
            "scale": scale,
            "out_w": w_input,
            "out_h": h_input,
            "crop": True,
        }
        if scale is None:
            param["crop"] = False
        img = image_cropper.crop(**param)
        prediction += model_test.predict(img, os.path.join(model_dir, model_name))


    label = np.argmax(prediction)
    value = prediction[0][label]/2
    if label == 1:
        print("Real input")
        return False
    else:
        print("Fake input")
        return True
