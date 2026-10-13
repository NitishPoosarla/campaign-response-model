"""05-marketing-campaign — 01_analysis.py

Campaign response analysis: who converts, by which channel/context, at what cost.

Outputs: processed dataset, kpis.json, segments, charts.
"""
from pathlib import Path
import json
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

_shared_root = Path(__file__).resolve().parent
while _shared_root != _shared_root.parent and not (_shared_root / "shared").is_dir():
    _shared_root = _shared_root.parent
sys.path.insert(0, str(_shared_root))  # callable from repo root or standalone checkout
from shared.utils import mpl_setup, save_png, save_json   # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent
OUT = PROJECT / "outputs"
mpl_setup()

CALL_COST = 2.50   # $ assumed marginal cost per dial (stated)
AVG_MARGIN = 120.0   # $ assumed contribution margin per subscribed customer (stated)


def main() -> None:
    (PROJECT / "data" / "processed").mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(PROJECT / "data" / "raw" / "bank-full.csv", sep=";")
    df["converted"] = (df["y"] == "yes").astype(int)

    conv = df.converted.mean()
    cost_of_all = len(df) * CALL_COST
    revenue_conv = df.converted.sum() * AVG_MARGIN
    kpis = {
        "contacts": int(len(df)),
        "conversion_rate": round(float(conv), 4),
        "conversions": int(df.converted.sum()),
        "assumed_call_cost": CALL_COST,
        "assumed_margin": AVG_MARGIN,
        "total_dial_cost": round(float(cost_of_all), 0),
        "campaign_revenue": round(float(revenue_conv), 0),
        "campaign_roi": round(float(revenue_conv / cost_of_all), 2),
        "response_rate_low_rate": round(float(
            df.loc[df.previous == 0, "converted"].mean()), 4),
        "response_rate_prior_success": round(float(
            df.loc[df.poutcome == "success", "converted"].mean()), 4),
        "avg_calls_per_contact": round(float(df.campaign.mean()), 2),
    }
    save_json(kpis, OUT / "kpis.json")

    segs = {}
    for col, name in [("job", "seg_job.csv"), ("month", "seg_month.csv"),
                      ("contact", "seg_contact.csv"), ("poutcome", "seg_poutcome.csv")]:
        s = df.groupby(col).agg(contacts=("converted", "count"),
                                conv_rate=("converted", "mean")).round(4)
        segs[col] = s
        s.to_csv(OUT / name)

    df.to_csv(PROJECT / "data" / "processed" / "bank_cleaned.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.4, 4))
    order = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    mo = segs["month"].reindex(order)
    ax.bar(mo.index, mo.conv_rate * 100, color="#0e7490")
    ax2 = ax.twinx()
    ax2.bar(mo.index, mo.contacts, alpha=.25, color="#e2584c", width=.5)
    ax2.set_ylabel("Contacts (light red)"); ax.set_ylabel("Conversion (%)")
    ax.set_title("Conversion rate vs campaign volume by month")
    save_png(fig, OUT / "charts" / "month_volume.png")

    fig, ax = plt.subplots(figsize=(7.2, 4))
    jb = segs["job"].sort_values("conv_rate")
    ax.barh(jb.index, jb.conv_rate * 100, color="#134e5e")
    ax.set_xlabel("Conversion (%)")
    ax.set_title("Conversion by profession — audience quality varies 5x")
    save_png(fig, OUT / "charts" / "conv_job.png")

    fig, ax = plt.subplots(figsize=(7.2, 4))
    ct = segs["contact"]
    ax.bar(ct.index, ct.conv_rate * 100, color="#d97706")
    ax.set_ylabel("Conversion (%)")
    ax.set_title("Channel: known vs unknown contact class")
    save_png(fig, OUT / "charts" / "conv_channel.png")
    print(json.dumps(kpis, indent=2))


if __name__ == "__main__":
    main()
