import os, warnings, absl.logging
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
absl.logging.set_verbosity(absl.logging.ERROR)
warnings.filterwarnings("ignore", category=UserWarning)
import mediapipe as mp
import numpy as np
import cv2
import tempfile
import time

mp_hands = mp.solutions.hands

def extract_keypoints_from_image(file):
    """Nhận file ảnh (werkzeug.FileStorage) → Mediapipe keypoints (x, y)"""
    start = time.time()
    print("📥 [mediapipe_service] Bắt đầu xử lý ảnh upload...")

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        file.save(tmp.name)
        img = cv2.imread(tmp.name)
    if img is None:
        print("❌ Không đọc được ảnh từ file.")
        return None

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    with mp_hands.Hands(static_image_mode=True, max_num_hands=1,
                        min_detection_confidence=0.5) as hands:
        result = hands.process(img_rgb)

        if not result.multi_hand_landmarks:
            print("⚠️ Không phát hiện bàn tay nào trong ảnh.")
            return None

        landmarks = result.multi_hand_landmarks[0]
        kps = np.array([[lm.x * 200, lm.y * 200] for lm in landmarks.landmark])
        print(f"✅ Đã trích xuất {len(kps)} keypoints trong {time.time() - start:.2f}s.")
        return kps
