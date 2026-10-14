"""05-marketing-campaign — 02_targeting_model.py

Who should the next dollar call? Gradient-boosted response model + costed call list.

Method: stratified split, AUC, decile lift table; budget scenarios priced with the
stated call cost and margin assumptions.

Outputs: outputs/model.json, outputs/target_scores.csv, outputs/deciles.csv, charts.
"""
from pathlib import Path
import json
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

_shared_root = Path(__file__).resolve().parent
while _shared_root != _shared_root.parent and not (_shared_root / "shared").is_dir():
    _shared_root = _shared_root.parent
sys.path.insert(0, str(_shared_root))  # callable from repo root or standalone checkout
from shared.utils import mpl_setup, save_png, save_json   # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent
mpl_setup()


def main() -> None:
    df = pd.read_csv(PROJECT / "data" / "processed" / "bank_cleaned.csv")
    y = df.converted
    X = pd.get_dummies(df.drop(columns=["y", "converted"]), drop_first=True).astype(float)

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=.25, stratify=y, random_state=7)
    gb = HistGradientBoostingClassifier(random_state=7)
    gb.fit(X_tr, y_tr)
    p_gb, p_lr = gb.predict_proba(X_te)[:, 1], None

    lr = LogisticRegression(max_iter=1500).fit(X_tr, y_tr)
    p_lr = lr.predict_proba(X_te)[:, 1]
    auc = (roc_auc_score(y_te, p_gb), roc_auc_score(y_te, p_lr))

    df["p_convert"] = gb.predict_proba(X)[:, 1]
    df.to_csv(PROJECT / "outputs" / "target_scores.csv", index=False)

    # decile lift on scored base
    d = df.sort_values("p_convert", ascending=False).reset_index(drop=True)
    n = len(d)
    d["decile"] = pd.cut(d.index, bins=10, labels=False) + 1
    dec = d.groupby("decile").agg(contacts=("converted", "count"),
                                  conv=("converted", "mean"),
                                  rev=("converted", lambda s: s.sum() * 120.0)).reset_index()
    dec.to_csv(PROJECT / "outputs" / "deciles.csv", index=False)

    kpis = {
        "auc_gb": round(float(auc[0]), 4),
        "auc_lr": round(float(auc[1]), 4),
        "base_conv": round(float(y.mean()), 4),
        "d1_conv": round(float(dec.iloc[0]["conv"]), 4),
        "d1_lift": round(float(dec.iloc[0]["conv"] / y.mean()), 2),
    }
    # budget scenarios: call the top-N deciles
    scen = []
    for k in range(1, 4):
        take = d[d.decile <= k]
        cost = len(take) * 2.5
        rev = take.converted.sum() * 120.0
        scen.append({"scenario": f"call deciles 1-{k}", "contacts": int(len(take)),
                     "cost": round(cost, 0), "revenue": round(rev, 0),
                     "roi": round(rev / cost, 2)})
    kpis["scenarios"] = scen
    save_json(kpis, PROJECT / "outputs" / "model.json")

    fig, ax = plt.subplots(figsize=(7, 3.9))
    ax.bar(dec.decile, dec.conv * 100, color="#0e7490")
    ax.axhline(y.mean() * 100, color="#e2584c", ls="--", label="baseline")
    ax.set_xlabel("Model decile (1 = most likely)"); ax.set_ylabel("Conversion (%)")
    ax.legend(); ax.set_title("Decile lift — the call list writes itself")
    save_png(fig, PROJECT / "outputs" / "charts" / "decile_lift.png")
    print(json.dumps(kpis, indent=2))


if __name__ == "__main__":
    main()
