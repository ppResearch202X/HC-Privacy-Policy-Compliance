"""
One‐shot RandomForest hyperparameter sweep on two embedding variants:
  • averaged (384-d)
  • zero‐padded (max_segs×384)

For each mode:
  1. Load & process into X (n_samples×D) and y
  2. GridSearchCV over RF params (macro-F1)
  3. Report best params + 5-fold Accuracy/Prec/Rec/F1
"""

import json
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    make_scorer
)

embed = "embed_RA_java"

# ─── CONFIG ────────────────────────────────────────────────────────────────
DATA_PATH = Path(f"HC-compatible_apps_{embed}.jsonl")
N_SPLITS   = 5
RANDOM_SEED = 42

RF_PARAMS = {
    "n_estimators":      [100, 200, 500],
    "max_depth":         [None, 10, 20, 50],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf":  [1, 2, 4]
}
# ────────────────────────────────────────────────────────────────────────────

def load_avg(path):
    X, y = [], []
    for line in path.open(encoding="utf-8"):
        obj = json.loads(line)
        vec = np.array(obj[embed], dtype=np.float32)
        if vec.size % 384 != 0:
            raise ValueError(f"{obj['package']} length {vec.size} not mult of 384")
        X.append(vec.reshape(-1, 384).mean(axis=0))
        y.append(obj["class"])
    return np.stack(X), np.array(y), "averaged (384-d)"

def load_padded(path):
    # figure out max segments
    segs = [(len(json.loads(l)[embed])//384) for l in path.open(encoding="utf-8")]
    max_segs = max(segs)
    X, y = [], []
    for line in path.open(encoding="utf-8"):
        obj = json.loads(line)
        full = np.array(obj[embed], dtype=np.float32)
        parts = full.reshape(-1, 384)
        pad = np.zeros((max_segs, 384), dtype=np.float32)
        pad[:parts.shape[0]] = parts
        X.append(pad.flatten())
        y.append(obj["class"])
    return np.stack(X), np.array(y), f"padded ({max_segs}×384={max_segs*384}-d)"

def rf_sweep(X, y, desc):
    print("\n" + "="*60)
    print(f"MODE: RandomForest on {desc}")
    print("="*60)
    scorer = make_scorer(
        lambda yt, yp: precision_recall_fscore_support(
            yt, yp, average="macro", zero_division=0
        )[2]
    )
    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_SEED)
    rf = RandomForestClassifier(class_weight="balanced", random_state=RANDOM_SEED)
    grid = GridSearchCV(
        rf,
        param_grid=RF_PARAMS,
        scoring=scorer,
        cv=cv,
        n_jobs=-1,
        verbose=1
    )
    grid.fit(X, y)

    best = grid.best_estimator_
    print("\n>>> Best RF params:", grid.best_params_)
    print(f">>> Best grid‐CV macro-F1: {grid.best_score_:.3f}")

    accs, precs, recs, f1s = [], [], [], []
    for train, test in cv.split(X, y):
        best.fit(X[train], y[train])
        pred = best.predict(X[test])
        accs.append(accuracy_score(y[test], pred))
        pr, rc, f1, _ = precision_recall_fscore_support(
            y[test], pred, average="macro", zero_division=0
        )
        precs.append(pr); recs.append(rc); f1s.append(f1)

    print(f"5-Fold Acc : {np.mean(accs):.3f}")
    print(f"5-Fold Prec: {np.mean(precs):.3f}")
    print(f"5-Fold Rec : {np.mean(recs):.3f}")
    print(f"5-Fold F1  : {np.mean(f1s):.3f}")

if __name__ == "__main__":
    X_avg, y_avg, d_avg = load_avg(DATA_PATH)
    rf_sweep(X_avg, y_avg, d_avg)

    X_pad, y_pad, d_pad = load_padded(DATA_PATH)
    rf_sweep(X_pad, y_pad, d_pad)
