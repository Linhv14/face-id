from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from lib.image_handler import read_base64, face_detector, compare_faces, resize_image, show_image, export_image, count_face_in_image
from lib.detect_face_in_image import detect_face_in_image
import os
import face_recognition
from silent_face.detect_faker import detect_faker

app = Flask(__name__)

CORS(app)
bcrypt = Bcrypt(app)

# Khai báo secret key
app.config["SECRET_KEY"] = os.urandom(24)

# Tạo kết nối với MongoDB
app.config["MONGO_URI"] = "mongodb://localhost:27017/face-id"

mongo = PyMongo(app)
print("Connected to MongoDB")

@app.route("/face-id/checkpoint/email", methods=["POST"])
def validate_email():
    email = request.json['email']

    try:
        collection = mongo.db.users
        user = collection.find_one({'email': email})
        if user:
            return jsonify({'result': 'Already exist'})
        else:
            return jsonify({'result': 'Not existed yet'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/face-id/register', methods=['POST'])
def register():
    # Lấy thông tin người dùng từ yêu cầu POST
    email = request.json['email']
    image = request.json['image']

    image_base64 = read_base64(image)

    number_of_face = count_face_in_image(image_base64)

    if number_of_face == 0:
        return jsonify({"error": "No face founded"})
    elif number_of_face > 1:
        return jsonify(({"error": "There are many faces"}))
    else:

        # Thêm người dùng mới vào cơ sở dữ liệu MongoDB
        user_collection = mongo.db.users
        new_user = user_collection.insert_one({
            'email': email,
            'image': image,
        })

        return jsonify({
            'result': 'Success'
        })

@app.route('/face-id/login', methods=['POST'])
def login():
    email = request.json['email']
    image = request.json['image']

    unknown_face = read_base64(image)
    unknown_face_path = "./store/unknown.jpg"

    # Kiểm tra nếu người dùng gian lận, sử dụng ảnh để đăng nhập
    is_fake = detect_faker(resize_image(unknown_face))
    result = {}
    if not is_fake:

        collection = mongo.db.users
        user = collection.find_one({'email': email})
        known_face = user['image']
        
        # Chuyển từ base64 sang np.array
        known_face = read_base64(known_face)
        known_face_path = "./store/known.jpg" 

        result = detect_face_in_image(known_face, unknown_face)
        result["email"] = email

    else:
        result = {"face_founded": False, "matched": False, "fake": True, "email": email}
    print(result)
    return jsonify(result)
if __name__ == "__main__":
    app.run()
