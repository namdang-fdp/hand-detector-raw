from flask import Blueprint, request, jsonify
from flasgger import swag_from
from app.services.classifier_service import classifier_predict
from app.services.mediapipe_service import extract_keypoints_from_image

predict_bp = Blueprint("predict_bp", __name__)

@swag_from({
    "tags": ["ASL Recognition"],
    "description": "Upload an image and predict ASL letter.",
    "consumes": ["multipart/form-data"],
    "parameters": [{
        "name": "file",
        "in": "formData",
        "type": "file",
        "required": True,
        "description": "Image file containing a hand sign"
    }],
    "responses": {
        200: {
            "description": "Prediction result",
            "examples": {
                "application/json": {
                    "prediction": "A",
                    "confidence": 0.92
                }
            }
        }
    }
})
@predict_bp.route("/predict/image", methods=["POST"])
def predict_image():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    kps = extract_keypoints_from_image(file)
    if kps is None:
        return jsonify({"error": "No hand detected"}), 200

    pred, conf = classifier_predict(kps)
    return jsonify({"prediction": pred, "confidence": round(conf, 3)})


@swag_from({
    "tags": ["ASL Recognition"],
    "description": "Stream webcam frames and return predictions (for frontend live mode)",
    "responses": {
        200: {"description": "Stream prediction frames"}
    }
})
@predict_bp.route("/predict/live", methods=["GET"])
def predict_live():
    # (Optional) — endpoint cung cấp real-time stream bằng OpenCV VideoCapture
    return jsonify({"message": "Webcam streaming handled on frontend"})
