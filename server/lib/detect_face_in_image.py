import face_recognition
import cv2

def detect_face_in_image(known_face, unknown_face):

    known_face_encoding = face_recognition.face_encodings(known_face)[0]
    unknown_face_encoding = face_recognition.face_encodings(unknown_face)
    print("Number of faces founded: ", len(unknown_face_encoding))
    if len(unknown_face_encoding) > 0:
        match_results = face_recognition.compare_faces([known_face_encoding], unknown_face_encoding[0], 0.4)

        if match_results[0]:
            return { "face_founded": True, "matched": True, "fake": False }
        else:
            return { "face_founded": True, "matched": False, "fake": False }
    return { "face_founded": False, "matched": False, "fake": False }
