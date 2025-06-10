
"""
One‐shot SVM model sweep over two different vector preparations:
  1) zero‐padded segments
  2) mean‐pooled (averaged) segments

For each mode, we:
  • load & process the embeddings into X (n_samples×D) and y
  • run GridSearchCV over several SVM variants
  • report best params + 5‐fold Acc/Prec/Rec/F1
"""
import json
import numpy as np
from pathlib import Path
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC, SVC, NuSVC
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support, make_scorer
)

embed = "embed_RA_java"

# ── CONFIG ─────────────────────────────────────────────────────────
DATA_PATH = Path(f"HC-compatible_apps_{embed}.jsonl")
N_SPLITS   = 5
RANDOM_SEED = 42
# ─────────────────────────────────────────────────────────────────

def load_data_padded(data_path):
    # 1st pass: find max #segments
    with data_path.open(encoding="utf-8") as f:
        counts = [len(json.loads(l)[embed])//384 for l in f]
    max_segs = max(counts)
    D = max_segs * 384

    X, y = [], []
    with data_path.open(encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            vec = np.array(obj[embed], dtype=np.float32)
            segs = vec.reshape(-1, 384)
            padded = np.zeros((max_segs, 384), dtype=np.float32)
            padded[:segs.shape[0]] = segs
            X.append(padded.flatten())
            y.append(obj["class"])
    return np.stack(X), np.array(y), f"padded ({D} dims)"

def load_data_avg(data_path):
    X, y = [], []
    with data_path.open(encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            vec = np.array(obj[embed], dtype=np.float32)
            if vec.size % 384 != 0:
                raise ValueError(f"{obj['package']} length {vec.size} not mult of 384")
            avg = vec.reshape(-1, 384).mean(axis=0)
            X.append(avg)
            y.append(obj["class"])
    return np.stack(X), np.array(y), "averaged (384 dims)"

def make_models():
    return {
        "LinearSVC": (
            LinearSVC(class_weight="balanced", max_iter=10_000, random_state=RANDOM_SEED),
            {"linearsvc__C": [0.01, 0.1, 1, 10]}
        ),
        "SVC-linear": (
            SVC(kernel="linear", class_weight="balanced", random_state=RANDOM_SEED),
            {"svc__C": [0.01, 0.1, 1, 10]}
        ),
        "SVC-rbf": (
            SVC(kernel="rbf", class_weight="balanced", random_state=RANDOM_SEED),
            {"svc__C": [0.1, 1, 10], "svc__gamma": ["scale", 0.001, 0.0001]}
        ),
        "SVC-poly": (
            SVC(kernel="poly", class_weight="balanced", random_state=RANDOM_SEED),
            {"svc__C": [0.1, 1, 10], "svc__degree": [2, 3], "svc__gamma": ["scale", 0.001]}
        ),
        "NuSVC-rbf": (
            NuSVC(kernel="rbf", class_weight="balanced", random_state=RANDOM_SEED),
            {"nusvc__nu": [0.25, 0.5], "nusvc__gamma": ["scale", 0.001]}
        ),
    }

def run_sweep(X, y, desc):
    print("\n" + "="*60)
    print(f"MODE: {desc}")
    print("="*60)

    scorer = make_scorer(lambda yt, yp: precision_recall_fscore_support(
        yt, yp, average="macro", zero_division=0
    )[2])

    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_SEED)

    for name, (estimator, grid) in make_models().items():
        pipe = make_pipeline(
            StandardScaler(with_mean=(desc!="padded")),  # center only if averaged
            estimator
        )
        gs = GridSearchCV(
            pipe, param_grid=grid, scoring=scorer,
            cv=cv, n_jobs=-1, verbose=0
        )
        gs.fit(X, y)

        best = gs.best_estimator_
        bp   = gs.best_params_
        bf1  = gs.best_score_

        # final 5-fold metrics
        accs = []; precs = []; recs = []; f1s = []
        for train, test in cv.split(X, y):
            best.fit(X[train], y[train])
            pred = best.predict(X[test])
            accs.append(accuracy_score(y[test], pred))
            pr, rc, f1, _ = precision_recall_fscore_support(
                y[test], pred, average="macro", zero_division=0
            )
            precs.append(pr); recs.append(rc); f1s.append(f1)

        print(f"\n{name}")
        print("-"*len(name))
        print(f" Best params       : {bp}")
        print(f" Grid-CV macro-F1  : {bf1:.3f}")
        print(f" Test 5-fold Acc   : {np.mean(accs):.3f}")
        print(f" Test 5-fold Prec  : {np.mean(precs):.3f}")
        print(f" Test 5-fold Rec   : {np.mean(recs):.3f}")
        print(f" Test 5-fold F1    : {np.mean(f1s):.3f}")

if __name__ == "__main__":
    # Padded
    Xp, yp, desc_p = load_data_padded(DATA_PATH)
    run_sweep(Xp, yp, desc_p)

    # Averaged
    Xa, ya, desc_a = load_data_avg(DATA_PATH)
    run_sweep(Xa, ya, desc_a)
