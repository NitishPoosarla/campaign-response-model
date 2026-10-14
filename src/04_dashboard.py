"""05-marketing-campaign — 04_dashboard.py — single-file campaign dashboard."""
from pathlib import Path
import json
import sys

import pandas as pd
import plotly.graph_objects as go

_shared_root = Path(__file__).resolve().parent
while _shared_root != _shared_root.parent and not (_shared_root / "shared").is_dir():
    _shared_root = _shared_root.parent
sys.path.insert(0, str(_shared_root))  # callable from repo root or standalone checkout
from shared.dashboard import build_dashboard   # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent
OUT = PROJECT / "outputs"


def main() -> None:
    kpis = json.loads((OUT / "kpis.json").read_text())
    model = json.loads((OUT / "model.json").read_text())
    dec = pd.read_csv(OUT / "deciles.csv")
    mo = pd.read_csv(OUT / "seg_month.csv", index_col=0)
    jb = pd.read_csv(OUT / "seg_job.csv", index_col=0)

    order = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    mo = mo.reindex(order)
    fig_mo = go.Figure()
    fig_mo.add_trace(go.Bar(x=mo.index, y=mo.conv_rate * 100, name="Conversion %", marker_color="#0e7490"))
    fig_mo.add_trace(go.Bar(x=mo.index, y=mo.contacts, name="Contacts", marker_color="#f0b9ad",
                            yaxis="y2", opacity=.5))
    fig_mo.update_layout(yaxis2=dict(overlaying="y", side="right", title="Contacts"),
                         xaxis_title="Month", yaxis_title="Conversion (%)")

    jb = jb.sort_values("conv_rate")
    fig_jb = go.Figure(go.Bar(y=jb.index, x=jb.conv_rate * 100, orientation="h", marker_color="#134e5e"))
    fig_jb.update_layout(xaxis_title="Conversion (%)")

    fig_dec = go.Figure(go.Bar(x=dec.decile, y=dec.conv * 100, marker_color="#0e7490",
                               text=[f"{c:.1%}" for c in dec.conv], textposition="outside"))
    fig_dec.update_layout(xaxis_title="Model decile", yaxis_title="Conversion (%)")

    build_dashboard(
        str(PROJECT / "dashboard" / "index.html"),
        title="Outbound Campaign Optimization — Response Analytics",
        subtitle=("Who converts, why, and where the next marketing dollar goes. "
                  "UCI Bank Marketing data, 45k direct dials, public; verified in Python."),
        badges=["Marketing", "Response model", "Decile lift", "Costed scenarios", "LLM narration"],
        kpis=[
            {"label": "Dials analysed", "value": f"{kpis['contacts']:,}"},
            {"label": "Conversion", "value": f"{kpis['conversion_rate']:.1%}"},
            {"label": "Top-decile lift", "value": f"{model['d1_lift']}x"},
            {"label": "Model AUC", "value": f"{model['auc_gb']:.2f}", "note": "GBDT on test"},
            {"label": "Best scenario ROI", "value": f"{model['scenarios'][0]['roi']}x",
             "note": model["scenarios"][0]["scenario"]},
        ],
        figures=[
            {"title": "Seasonality: conversion vs dial volume", "sub": "the calendar rebalance is free", "fig": fig_mo},
            {"title": "Conversion by profession", "sub": "audience quality spread", "fig": fig_jb},
            {"title": "Decile lift", "sub": "target scores from the response model", "fig": fig_dec},
        ],
        recommendations=[
            f"Call the model's top decile first ({model['scenarios'][0]['scenario']}: "
            f"{model['scenarios'][0]['contacts']:,} dials, ROI {model['scenarios'][0]['roi']}x at stated cost assumptions).",
            "Shift 30% of peak-month (May) budget into the autumn shoulder months where conversion peaks while dial volume collapses.",
            "Maintain a prioritized 'known-number' list — known contact class materially outperforms unknown.",
            "A/B test the cap on attempts per contact (avg %.1f calls here) before raising call counts further." % kpis["avg_calls_per_contact"],
        ],
        footer=("Data: UCI Bank Marketing (public, no PII). AI narrates verified metrics only. "
                "Stated assumptions: $2.50/dial, $120 contribution margin per subscriber."),
    )
    print("dashboard written")


if __name__ == "__main__":
    main()
