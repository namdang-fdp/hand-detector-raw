import os
os.environ["MEDIAPIPE_USE_GPU"] = "true" # dung GPU thay vi CPU
os.environ["CUDA_VISIBLE_DEVICES"] = "0" # dung GPU so 0
os.environ["OMP_NUM_THREADS"] = "4" # gioi han so luong CPU
os.environ["TF_XLA_FLAGS"] = "--tf_xla_enable_xla_devices" # toi uu toc do bang JIT Compiler trong tensorflow

# tat log rac
import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)

import cv2 # doc anh csv
import csv # ghi ket qua ra file csv
import mediapipe as mp # thu vien media pipe, trich xuat keypoint tu ban tay
import numpy as np # xu ly toan hoc, mang
from tqdm import tqdm # tao thanh progress bar
import concurrent.futures  # chay nhieu threa song song
from time import time  # do thoi gian chay

DATASET_DIR = os.path.expanduser("~/Downloads/asl_alphabet_train/asl_alphabet_train/asl_alphabet_train/")
OUTPUT_CSV = "/home/namdang-fdp/Projects/hand-detect-ai/keypoints_dataset_full_mediapipe.csv"
MAX_WORKERS = 8

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.3
)

columns = ["label"] + [f"x{i+1}" for i in range(21)] + [f"y{i+1}" for i in range(21)]

def extract_landmarks_from_image(img):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    if not results.multi_hand_landmarks:
        return None
    landmarks = results.multi_hand_landmarks[0]
    pts = np.array([[lm.x * 200, lm.y * 200] for lm in landmarks.landmark])
    return pts


def read_image(path):
    img = cv2.imread(path)
    return path, img


def main():
    print("🚀 Starting full A–Z extraction with GPU optimization...\n")
    start = time()
    total, fail = 0, 0
    all_rows = []

    classes = sorted([d for d in os.listdir(DATASET_DIR)
                      if os.path.isdir(os.path.join(DATASET_DIR, d))])

    for label in classes:
        folder = os.path.join(DATASET_DIR, label)
        img_files = [f for f in os.listdir(folder)
                     if f.lower().endswith((".jpg", ".jpeg", ".png"))]

        print(f"\n📁 Extracting {label}: {len(img_files)} images")

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(read_image, os.path.join(folder, f)) for f in img_files]
            for future in tqdm(concurrent.futures.as_completed(futures),
                               total=len(img_files),
                               desc=f"Loading {label}",
                               ncols=80):
                img_path, img = future.result()
                if img is None:
                    fail += 1
                    continue

                pts = extract_landmarks_from_image(img)
                if pts is None:
                    fail += 1
                    continue

                row = [label] + pts[:, 0].tolist() + pts[:, 1].tolist()
                all_rows.append(row)
                total += 1

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(all_rows)

    duration = time() - start
    print("\n==========================================")
    print(f"✅ Saved {total:,} samples from {len(classes)} classes")
    print(f"⚠️ Skipped {fail:,} failed detections")
    print(f"🕒 Total time: {duration/60:.1f} minutes ({total/duration:.1f} img/s)")
    print(f"💾 Output CSV: {OUTPUT_CSV}")
    print("==========================================\n")


if __name__ == "__main__":
    main()

