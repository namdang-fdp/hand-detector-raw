from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flasgger import Swagger
import base64, cv2, numpy as np, mediapipe as mp, os, json
from app.services.classifier_service import classifier_predict

# =====================================
# ⚙️ INIT
# =====================================
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
swagger = Swagger(app)

mp_hands = mp.solutions.hands
BENCHMARK_PATH = "app/models/model_benchmark.json"

# =====================================
# 🔧 UTIL
# =====================================
def decode_base64_image(base64_string: str):
    """Decode base64 image string -> OpenCV image."""
    try:
        img_data = base64.b64decode(base64_string.split(",")[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except Exception:
        return None


def extract_keypoints(img):
    """Extract 21 Mediapipe hand keypoints from an image."""
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    with mp_hands.Hands(
        static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5
    ) as hands:
        result = hands.process(img_rgb)
        if not result.multi_hand_landmarks:
            return None
        lm = result.multi_hand_landmarks[0]
        return np.array([[p.x * 200, p.y * 200] for p in lm.landmark])


# =====================================
# 🔌 SOCKET EVENTS (Realtime)
# =====================================
@socketio.on("connect")
def on_connect():
    print("✅ [socket_service] Client connected")
    emit("server_status", {"status": "connected"})


@socketio.on("disconnect")
def on_disconnect():
    print("❌ [socket_service] Client disconnected")


@socketio.on("frame")
def handle_frame(base64_frame):
    img = decode_base64_image(base64_frame)
    if img is None:
        emit("prediction", {"prediction": "INVALID", "confidence": 0})
        return

    kps = extract_keypoints(img)
    if kps is None:
        emit("prediction", {"prediction": "NO_HAND", "confidence": 0})
        return

    pred, conf = classifier_predict(kps)
    emit("prediction", {"prediction": pred, "confidence": conf})


# =====================================
# 🧠 REST API (Swagger)
# =====================================

@app.route("/predict_image", methods=["POST"])
def predict_image():
    """
    Upload an image and get ASL prediction.
    ---
    tags:
      - Hand Sign Classification
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: Image file to analyze
    responses:
      200:
        description: Prediction result
        schema:
          type: object
          properties:
            prediction:
              type: string
              example: "A"
            confidence:
              type: number
              example: 0.93
      400:
        description: Invalid input
    """
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    file_bytes = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if img is None:
        return jsonify({"error": "Invalid image"}), 400

    kps = extract_keypoints(img)
    if kps is None:
        return jsonify({"prediction": "NO_HAND", "confidence": 0.0})

    pred, conf = classifier_predict(kps)
    return jsonify({"prediction": pred, "confidence": conf})


@app.route("/healthz", methods=["GET"])
def healthz():
    """
    Health check endpoint.
    ---
    tags:
      - System
    responses:
      200:
        description: Health check OK
        schema:
          type: object
          properties:
            status:
              type: string
              example: "ok"
            msg:
              type: string
              example: "ASL backend is running"
    """
    return jsonify({"status": "ok", "msg": "ASL backend is running"})


@app.route("/stats", methods=["GET"])
def get_stats():
    """
    Get real benchmark statistics from trained models.
    ---
    tags:
      - Analytics
    responses:
      200:
        description: Benchmark data for visualization
        schema:
          type: object
          properties:
            avg_accuracy:
              type: number
              example: 0.97
            total_models:
              type: integer
              example: 3
            benchmark_results:
              type: array
              items:
                type: object
                properties:
                  model:
                    type: string
                    example: "RandomForest (Calibrated)"
                  accuracy:
                    type: number
                    example: 0.98
                  f1:
                    type: number
                    example: 0.97
                  precision:
                    type: number
                    example: 0.97
                  recall:
                    type: number
                    example: 0.97
                  train_time:
                    type: number
                    example: 113.40
    """
    if not os.path.exists(BENCHMARK_PATH):
        return jsonify({"error": "Benchmark file not found"}), 404

    with open(BENCHMARK_PATH, "r") as f:
        data = json.load(f)

    results = data.get("benchmark_results", [])
    if not results:
        return jsonify({"error": "No benchmark data found"}), 404

    avg_acc = sum(m["accuracy"] for m in results) / len(results)
    return jsonify({
        "avg_accuracy": avg_acc,
        "total_models": len(results),
        "benchmark_results": results
    })


# =====================================
# 🩵 MAIN
# =====================================
if __name__ == "__main__":
    print("🚀 ASL WebSocket + REST backend running on http://localhost:8080")
    print("📘 Swagger UI: http://localhost:8080/apidocs")
    socketio.run(app, host="0.0.0.0", port=8080, allow_unsafe_werkzeug=True)

