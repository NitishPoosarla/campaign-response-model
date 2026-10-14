"""05-marketing-campaign — 03_ai_insights.py — measured AI narrative for the CMO brief."""
from pathlib import Path
import csv
import json
import sys

_shared_root = Path(__file__).resolve().parent
while _shared_root != _shared_root.parent and not (_shared_root / "shared").is_dir():
    _shared_root = _shared_root.parent
sys.path.insert(0, str(_shared_root))  # callable from repo root or standalone checkout
from shared import llm   # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent
OUT = PROJECT / "outputs"


def main() -> None:
    kpis = json.loads((OUT / "kpis.json").read_text())
    model = json.loads((OUT / "model.json").read_text())
    with open(OUT / "deciles.csv") as f:
        dec = list(csv.DictReader(f))
    drivers = {
        "Untargeted calling is a leak": (f"Baseline conversion {kpis['conversion_rate']:.1%} over "
                                         f"{kpis['contacts']:,} dials; AI targeting lifts the top decile "
                                         f"{model['d1_lift']}x."),
        "Timing beats volume": ("May = peak contacts at bottom-tier conversion; "
                                "autumn shoulder months convert while dialing volume collapses — "
                                "rebalancing the calendar is free."),
        "Audience quality spread": ("Profession segments differ up to ~5x in conversion; "
                                    "knowing the list (contact class) outperforms unknown."),
        "Costed scenarios": json.dumps(model["scenarios"]),
    }
    prompt = f"""You are briefing a bank CMO on the outbound campaign. Use ONLY verified metrics.
Deliver: (1) two-sentence verdict, (2) ranked actions with $, (3) what to A/B next.
Metrics: {json.dumps({**kpis, **model, "deciles": dec}, indent=1)}"""
    md = llm.write_insights(str(OUT / "insights.md"), "Outbound campaign optimization", kpis, drivers, prompt)
    print(md[:900])


if __name__ == "__main__":
    main()
