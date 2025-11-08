#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 2️⃣: Convert raw keypoints (x,y) → normalized 57-dim feature vector
Input : keypoints_dataset_full_mediapipe.csv
Output: feature_dataset.csv
"""

import pandas as pd
import numpy as np
from tqdm import tqdm
from features import extract_features 

# ======================
# ⚙️ CONFIG
# ======================
CSV_INPUT = "/home/namdang-fdp/Projects/hand-detect-ai/keypoints_dataset_full_mediapipe.csv"
CSV_OUTPUT = "/home/namdang-fdp/Projects/hand-detect-ai/feature_dataset.csv"

# ======================
# 📦 LOAD DATA
# ======================
print(f"🚀 Loading raw dataset: {CSV_INPUT}")
df = pd.read_csv(CSV_INPUT)
print(f"✅ Loaded {len(df):,} samples")

# ======================
# 🧩 CONVERT TO FEATURES
# ======================
rows = []
for _, row in tqdm(df.iterrows(), total=len(df), desc="Extracting features"):
    label = row["label"]
    # Tạo mảng (21,2)
    kps = np.array([[row[f"x{i+1}"], row[f"y{i+1}"]] for i in range(21)], dtype=np.float32)
    feats = extract_features(kps)
    rows.append([label] + feats.tolist())

# ======================
# 💾 SAVE FEATURE CSV
# ======================
cols = ["label"] + [f"f{i+1}" for i in range(len(rows[0]) - 1)]
out_df = pd.DataFrame(rows, columns=cols)
out_df.to_csv(CSV_OUTPUT, index=False)

print(f"\n💾 Saved normalized feature dataset to:")
print(f"   {CSV_OUTPUT}")
print(f"✅ Total samples: {len(out_df):,} | Feature dims: {len(cols)-1}")
