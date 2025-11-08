from joblib import load
import numpy as np
import os
import sys
import time
import warnings
warnings.filterwarnings("ignore", message="X does not have valid feature names")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from features import extract_features

MODEL_PATH = "app/models/rf_mediapipe_feature_calibrated.pkl"
SCALER_PATH = "app/models/feature_scaler.pkl"

print(f"🧠 [classifier_service] Đang load model: {MODEL_PATH}")
clf = load(MODEL_PATH)
scaler = load(SCALER_PATH)
print(f"✅ [classifier_service] Model đã sẵn sàng ({len(clf.classes_)} classes)\n")

TRAIN_X_MEAN, TRAIN_Y_MEAN, TRAIN_PALM = 154.22, 124.29, 68.35

def normalize_keypoints(kps):
    wrist = kps[0].copy()
    kps -= wrist
    palm = np.mean([np.linalg.norm(kps[j]) for j in [5, 9, 13, 17]]) + 1e-6
    scale = TRAIN_PALM / palm
    scale = np.clip(scale, 0.8, 2.0)
    kps *= scale
    kps[:, 0] += TRAIN_X_MEAN
    kps[:, 1] += TRAIN_Y_MEAN
    return kps

def classifier_predict(kps):
    start = time.time()
    feats = extract_features(kps).reshape(1, -1)
    print(f"🧩 [classifier_service] Trích đặc trưng: {feats.shape} (57 features)")

    X_input = scaler.transform(feats)
    print("📊 [classifier_service] Đã chuẩn hóa dữ liệu, bắt đầu predict...")

    probs = clf.predict_proba(X_input)[0]
    pred_idx = int(np.argmax(probs))
    pred_label = clf.classes_[pred_idx]
    conf = float(probs[pred_idx])

    print(f"✅ [classifier_service] Predict={pred_label} ({conf:.3f}) | Thời gian={time.time()-start:.2f}s")
    return pred_label, conf
