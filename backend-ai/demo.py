#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Live ASL Recognition Demo (Mediapipe + Calibrated RandomForest on 57-dim features)
"""

import os
os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["MEDIAPIPE_USE_GPU"] = "true"

import cv2
import mediapipe as mp
import numpy as np
import collections
import time
import pandas as pd
from joblib import load
from features import extract_features  # ✅ dùng lại đúng feature pipeline 57-dim

# ======================
# ⚙️ CONFIG
# ======================
MODEL_PATH  = "/home/namdang-fdp/Projects/hand-detect-ai/rf_mediapipe_feature_calibrated.pkl"
SCALER_PATH = "/home/namdang-fdp/Projects/hand-detect-ai/feature_scaler.pkl"

PROB_THRESHOLD = 0.45          # < ngưỡng → gán UNKNOWN
SMOOTH_WINDOW  = 7             # số frame để lấy mode ổn định
DRAW_COLOR     = (0, 255, 0)   # nhãn dự đoán
FPS_EVERY_N    = 10            # cập nhật FPS mỗi N frame
LANDMARK_SCALE = 200.0         # giống lúc build dataset

# ======================
# 🧩 INIT MODELS
# ======================
print("🚀 Loading classifier & scaler...")
clf = load(MODEL_PATH)
scaler = load(SCALER_PATH)
print(f"✅ Loaded model with {len(getattr(clf, 'classes_', []))} classes")

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.40,
    min_tracking_confidence=0.30
)
mp_drawing = mp.solutions.drawing_utils

# ======================
# 🔧 HELPERS
# ======================
def draw_label(img, text, org, color=(0, 255, 0)):
    x, y = org
    fs, th = 1.1, 2
    (tw, tht), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fs, th)
    cv2.rectangle(img, (x, y - tht - 12), (x + tw + 10, y), (0, 0, 0), -1)
    cv2.putText(img, text, (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, fs, color, th, cv2.LINE_AA)

def features_to_df(feats: np.ndarray) -> pd.DataFrame:
    """
    Trả về DataFrame 1 hàng với tên cột f1..f57 để
    khớp với StandardScaler đã fit trên DataFrame (tránh warning).
    """
    n = feats.shape[-1]
    cols = [f"f{i+1}" for i in range(n)]
    return pd.DataFrame([feats.astype(np.float32)], columns=cols)

# ======================
# 🎥 MAIN LOOP
# ======================
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open webcam.")
        return

    # tuỳ camera:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    history = collections.deque(maxlen=SMOOTH_WINDOW)
    frame_count = 0
    last_time = time.time()

    print("🎬 Live demo started (press 'q' to quit)\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)  # lật gương
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            # chỉ lấy bàn tay đầu tiên (max_num_hands=1)
            hand_landmarks = results.multi_hand_landmarks[0]

            # === 1) Lấy 21 keypoints theo đúng scale như lúc build dataset
            kps = np.array(
                [[lm.x * LANDMARK_SCALE, lm.y * LANDMARK_SCALE] for lm in hand_landmarks.landmark],
                dtype=np.float32
            )  # shape (21, 2)

            # === 2) Trích 57-dim features đúng pipeline training
            feats = extract_features(kps)                     # shape (57,)
            X_df  = features_to_df(feats)                    # DataFrame 1x57
            X_std = scaler.transform(X_df)                   # chuẩn hoá như lúc train

            # === 3) Dự đoán
            probs = clf.predict_proba(X_std)[0]
            pred_idx = int(np.argmax(probs))
            pred_label = clf.classes_[pred_idx]
            prob = float(probs[pred_idx])

            if prob < PROB_THRESHOLD:
                pred_label = "UNKNOWN"

            # === 4) Smoothing kết quả
            history.append(pred_label)
            stable = max(set(history), key=history.count)

            # === 5) Vẽ landmarks + label
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            h, w, _ = frame.shape
            x0 = int(hand_landmarks.landmark[0].x * w)
            y0 = int(hand_landmarks.landmark[0].y * h)
            draw_label(frame, f"{stable} ({prob*100:.1f}%)", (x0 + 20, max(30, y0 - 10)), DRAW_COLOR)

            # Log nhẹ cho debug
            print(f"[Frame] Pred={pred_label}, Stable={stable}, Prob={prob:.3f}")
        else:
            history.append("NO_HAND")
            print("🖐️ No hand detected.")

        # === FPS overlay
        frame_count += 1
        if frame_count >= FPS_EVERY_N:
            now = time.time()
            fps = frame_count / (now - last_time)
            last_time, frame_count = now, 0
            cv2.putText(frame, f"FPS: {fps:.1f}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)

        cv2.imshow("ASL Recognition (Mediapipe + RF Calibrated, 57 features)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\n👋 Demo ended.")

if __name__ == "__main__":
    main()
