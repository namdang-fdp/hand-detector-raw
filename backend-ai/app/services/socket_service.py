import base64
import cv2
import numpy as np
import os
import absl.logging
import warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # 0=all, 1=info, 2=warning, 3=error only
absl.logging.set_verbosity(absl.logging.ERROR)
warnings.filterwarnings("ignore", category=UserWarning)
import mediapipe as mp
import time
from app.services.classifier_service import classifier_predict
from flask_socketio import emit

mp_hands = mp.solutions.hands

def decode_base64_image(base64_string):
    """Chuyển base64 string → numpy array (ảnh BGR)"""
    try:
        img_data = base64.b64decode(base64_string.split(",")[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        print(f"📸 [socket_service] Ảnh decode thành công: shape={img.shape}")
        return img
    except Exception as e:
        print(f"❌ [socket_service] Lỗi decode base64: {e}")
        return None

def extract_keypoints(img):
    """Extract 21 keypoints bằng Mediapipe"""
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    with mp_hands.Hands(static_image_mode=True, max_num_hands=1,
                        min_detection_confidence=0.5) as hands:
        result = hands.process(img_rgb)

        if not result.multi_hand_landmarks:
            print("⚠️ [socket_service] Không phát hiện bàn tay.")
            return None

        lm = result.multi_hand_landmarks[0]
        kps = np.array([[p.x * 200, p.y * 200] for p in lm.landmark])
        print(f"🖐️ [socket_service] Phát hiện {len(kps)} keypoints.")
        return kps

def register_socket_events(socketio):
    """Đăng ký sự kiện cho Flask-SocketIO"""

    @socketio.on("connect")
    def handle_connect():
        print("✅ [socket_service] Client connected")

    @socketio.on("disconnect")
    def handle_disconnect():
        print("❌ [socket_service] Client disconnected")

    @socketio.on("frame")
    def handle_frame(data):
        """Nhận 1 frame base64 từ frontend"""
        print(f"📡 [socket_service] Nhận frame từ FE, kích thước: {len(data)} bytes")

        start = time.time()
        img = decode_base64_image(data)
        if img is None:
            emit("prediction", {"error": "Invalid image data"})
            return

        kps = extract_keypoints(img)
        if kps is None:
            emit("prediction", {"prediction": "NO_HAND", "confidence": 0.0})
            print(f"⏱️ [socket_service] Không có tay — mất {time.time()-start:.2f}s\n")
            return

        pred, conf = classifier_predict(kps)
        print(f"🎯 [socket_service] Dự đoán: {pred} ({conf:.2f}) | Tổng thời gian {time.time()-start:.2f}s\n")

        emit("prediction", {"prediction": pred, "confidence": round(conf, 3)})
