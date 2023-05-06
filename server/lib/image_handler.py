import base64
import numpy as np
import cv2
import face_recognition
from flask import jsonify

def show_image(image):
    cv2.imshow("Image", image)
    cv2.waitKey(0)

def read_base64(uri):
    np_arr = np.fromstring(base64.b64decode(uri), np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)


def export_image(path, image):
    cv2.imwrite(path, image)

def face_detector(image):
    unknown_face_encodings = face_recognition.face_encodings(image)
    print("Number of faces founded:" , len(unknown_face_encodings))
    if len(unknown_face_encodings) > 0:
        return True

    return False

def count_face_in_image(image):
    unknown_face_encodings = face_recognition.face_encodings(image)
    return len(unknown_face_encodings)

def compare_faces(unknown_face_encodings, known_face_encoding):
    if len(unknown_face_encodings) > 0:
        # See if the first face in the uploaded image matches the known face of Obama

        match_results = face_recognition.compare_faces([known_face_encoding], unknown_face_encodings[0])
        if all(match_results[0]):
            return True
    return False

def resize_image(image):
    return cv2.resize(image, (300,400))