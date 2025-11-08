import pandas as pd
import numpy as np
import time, json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

# ======================
# ⚙️ CONFIG
# ======================
CSV_PATH = "/home/namdang-fdp/Projects/hand-detect-ai/feature_dataset.csv"
OUTPUT_JSON = "/home/namdang-fdp/Projects/hand-detect-ai/model_benchmark.json"
OUTPUT_CSV  = "/home/namdang-fdp/Projects/hand-detect-ai/model_benchmark.csv"

# ======================
# 📦 LOAD DATA
# ======================
print("🚀 Loading feature dataset...")
df = pd.read_csv(CSV_PATH)
df = df[~df["label"].isin({"space", "nothing", "del"})].reset_index(drop=True)
X = df.drop(columns=["label"])
y = df["label"]
print(f"✅ Loaded {len(df):,} samples, {df['label'].nunique()} classes.")

# ======================
# 🔀 SPLIT & SCALE
# ======================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# ======================
# ⚡ BENCHMARK FUNCTION
# ======================
def benchmark_model(name, model):
    print(f"\n🚀 Training {name} ...")
    start = time.time()
    model.fit(X_train, y_train)
    t = time.time() - start
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="macro")
    prec = precision_score(y_test, y_pred, average="macro")
    rec = recall_score(y_test, y_pred, average="macro")

    print(f"✅ {name}: acc={acc:.4f} | f1={f1:.4f} | time={t:.1f}s")
    return {"model": name, "accuracy": acc, "precision": prec, "recall": rec, "f1": f1, "train_time": t}

results = []

# 🌲 Random Forest (Calibrated)
rf = RandomForestClassifier(
    n_estimators=400,
    max_depth=25,
    class_weight="balanced_subsample",
    n_jobs=-1,
    random_state=42
)
rf_cal = CalibratedClassifierCV(rf, method="sigmoid", cv=3)
results.append(benchmark_model("RandomForest (Calibrated)", rf_cal))

# 📉 Logistic Regression (lightly regularized)
lr = LogisticRegression(
    penalty='l1',
    solver='saga',
    C=0.7,
    max_iter=500,
    n_jobs=-1,
    random_state=42
)
results.append(benchmark_model("Logistic Regression (L1)", lr))

# 🌿 Extra Trees (shallow version)
et = ExtraTreesClassifier(
    n_estimators=150,
    max_depth=15,
    min_samples_split=5,
    n_jobs=-1,
    random_state=42
)
results.append(benchmark_model("Extra Trees (Shallow)", et))

# ======================
# 💾 SAVE RESULTS
# ======================
pd.DataFrame(results).to_csv(OUTPUT_CSV, index=False)
with open(OUTPUT_JSON, "w") as f:
    json.dump({"benchmark_results": results}, f, indent=2)

print("\n==============================================")
print("✅ BENCHMARK COMPLETED")
for r in results:
    print(f"🔹 {r['model']:<25} acc={r['accuracy']:.3f} | f1={r['f1']:.3f} | time={r['train_time']:.1f}s")
print("💾 Saved to:")
print(f"   - {OUTPUT_JSON}")
print(f"   - {OUTPUT_CSV}")
print("==============================================")
