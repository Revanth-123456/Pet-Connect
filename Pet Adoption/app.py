from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
import numpy as np
from PIL import Image
from pymongo import MongoClient
from sklearn.metrics.pairwise import cosine_similarity
from torchvision import models, transforms
import torch

# Initialize Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["pet_recognition"]
found_collection = db["found_pets"]

# Pretrained model (for image feature extraction)
model = models.resnet18(pretrained=True)
model = torch.nn.Sequential(*(list(model.children())[:-1]))  # remove classifier layer
model.eval()

# Image transform
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# Helper: Convert base64 → PIL Image
def base64_to_image(base64_str):
    base64_str = base64_str.split(",")[-1]
    image_data = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(image_data)).convert("RGB")

# Helper: Extract features
def extract_features(img):
    img_tensor = transform(img).unsqueeze(0)
    with torch.no_grad():
        features = model(img_tensor).squeeze().numpy().flatten()
    return features / np.linalg.norm(features)

@app.route("/report/", methods=["POST"])
def report_pet():
    data = request.json
    report_type = data.get("report_type")
    image_b64 = data.get("image")
    city = data.get("city")
    name = data.get("name", "")
    phone_number = data.get("phone_number", "")

    if not image_b64 or not city:
        return jsonify({"error": "Missing required fields"}), 400

    img = base64_to_image(image_b64)
    features = extract_features(img).tolist()

    # --- FOUND PET ---
    if report_type == "found":
        found_collection.insert_one({
            "name": name,
            "phone_number": phone_number,
            "city": city,
            "found_image": image_b64,
            "features": features
        })
        return jsonify({"message": "Found pet report stored successfully!"}), 200

    # --- LOST PET ---
    elif report_type == "lost":
        matches = []
        found_pets = list(found_collection.find())

        if not found_pets:
            return jsonify({"matches": []}), 200

        lost_features = np.array(features).reshape(1, -1)
        similarities = []

        for pet in found_pets:
            found_features = np.array(pet["features"]).reshape(1, -1)
            score = cosine_similarity(lost_features, found_features)[0][0]
            similarities.append((score, pet))

        # Sort and filter by threshold (top similar ones)
        similarities = sorted(similarities, key=lambda x: x[0], reverse=True)
        for score, pet in similarities:
            if score > 0.8:  # similarity threshold
                matches.append({
                    "name": pet.get("name", ""),
                    "phone_number": pet.get("phone_number", ""),
                    "city": pet.get("city", ""),
                    "found_image": pet.get("found_image", "")
                })

        return jsonify({"matches": matches}), 200

    else:
        return jsonify({"error": "Invalid report type"}), 400


if __name__ == "__main__":
    app.run(host="localhost", port=8001, debug=True)
