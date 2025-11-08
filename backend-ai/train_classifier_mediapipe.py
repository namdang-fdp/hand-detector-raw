#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 3️⃣: Train RandomForest on normalized 57-dim features
Input : feature_dataset.csv
Output: rf_mediapipe_feature_calibrated.pkl + feature_scaler.pkl
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from joblib import dump
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ======================
# ⚙️ CONFIG
# ======================
CSV_PATH = "/home/namdang-fdp/Projects/hand-detect-ai/feature_dataset.csv"
MODEL_PATH = "/home/namdang-fdp/Projects/hand-detect-ai/rf_mediapipe_feature_calibrated.pkl"
SCALER_PATH = "/home/namdang-fdp/Projects/hand-detect-ai/feature_scaler.pkl"

# ======================
# 📦 LOAD DATA
# ======================
print("🚀 Loading normalized feature dataset...")
df = pd.read_csv(CSV_PATH)

# 🔹 Giữ lại 26 ký tự A–Z
exclude = {"space", "nothing", "del"}
df = df[~df["label"].isin(exclude)].reset_index(drop=True)

print(f"✅ Loaded {len(df):,} samples, {df['label'].nunique()} classes: {sorted(df['label'].unique())}")

X = df.drop(columns=["label"])
y = df["label"]

# ======================
# 🔀 SPLIT DATA
# ======================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ======================
# ⚙️ FEATURE SCALING
# ======================
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ======================
# 🌲 TRAIN RANDOM FOREST
# ======================
print("\n🧠 Training RandomForest (on normalized features)...")
rf = RandomForestClassifier(
    n_estimators=400,
    max_depth=25,
    n_jobs=-1,
    random_state=42,
    class_weight="balanced_subsample",
)
rf.fit(X_train_scaled, y_train)

# ======================
# 🎯 CALIBRATION
# ======================
print("\n🔧 Calibrating probabilities (sigmoid)...")
clf = CalibratedClassifierCV(rf, method="sigmoid", cv=3)
clf.fit(X_train_scaled, y_train)

# ======================
# 📊 EVALUATION
# ======================
print("\n📊 Evaluating on test set...")
y_pred = clf.predict(X_test_scaled)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Accuracy: {acc*100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, digits=3))

# ======================
# 🔍 CONFUSION MATRIX
# ======================
plt.figure(figsize=(16, 14))
cm = confusion_matrix(y_test, y_pred, labels=clf.classes_)
sns.heatmap(cm, annot=False, fmt="d", cmap="Blues",
            xticklabels=clf.classes_, yticklabels=clf.classes_)
plt.title(f"Confusion Matrix (Accuracy={acc*100:.2f}%)")
plt.xlabel("Predicted")
plt.ylabel("True")
plt.tight_layout()
plt.savefig(os.path.join(os.path.dirname(MODEL_PATH), "confusion_matrix_rf_feature_calibrated.png"))
plt.close()

# ======================
# 💾 SAVE MODEL
# ======================
dump(clf, MODEL_PATH)
dump(scaler, SCALER_PATH)
print(f"\n💾 Model saved to {MODEL_PATH}")
print(f"💾 Scaler saved to {SCALER_PATH}")
print("✅ Training complete! Ready for demo.\n")
