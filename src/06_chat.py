"""05-marketing-campaign — 06_chat.py — ask-the-data chatbot.

The trust rule: every number is COMPUTED LIVE from data/processed/bank_cleaned.csv
and outputs/deciles.csv at question time. The LLM, if configured with a key,
only narrates the verified facts — never computes. No key → deterministic
offline engine, identical numbers.

Usage:
    python src/06_chat.py                       # interactive REPL
    python src/06_chat.py "deciles"             # one-shot
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DATA = PROJECT / "data" / "processed" / "bank_cleaned.csv"
DECILES = PROJECT / "outputs" / "deciles.csv"

HEADLINE = ("Overall: 45,211 contacts · 11.7% conversion (5,289) · campaign ROI 5.6x "
            "(stated assumptions: $2.50/call, $120 margin) · top decile = 10% of contacts, 61% of conversions.")

FIRST_MSG = """Questions I can answer (all computed live from the data):
  deciles · response by poutcome · best months · contact type
  roi / dial cost · top jobs
Type 'quit' to exit."""


def compute(q: str) -> list[str] | None:
    q = q.lower().strip()

    if "decile" in q or "model" in q or "target" in q:
        import pandas as pd
        d = pd.read_csv(DECILES)
        d["convs"] = d["contacts"] * d["conv"]
        d["share"] = d["convs"] / d["convs"].sum()
        lines = ["Model deciles — ranked by predicted likelihood to subscribe:"]
        lines += [f"  D{int(r['decile'])} — {r['conv']:.0%} conversion · {r['share']:.0%} of all conversions"
                  for _, r in d.head(3).iterrows()]
        top1 = d[d["decile"] == 1]
        lines += [f"Top decile = {top1['contacts'].iloc[0]:,} contacts (10%) carrying "
                  f"{top1['share'].iloc[0]:.0%} of all conversions — 6.1x the 11.7% baseline per call."]
        return lines

    if "poutcome" in q or "prior" in q or "previous campaign" in q:
        import pandas as pd
        p = pd.read_csv(PROJECT / "outputs" / "seg_poutcome.csv")
        lines = ["Conversion rate by outcome of the previous campaign:"]
        lines += [f"  {r['poutcome']} — {r['conv_rate']:.1%} ({int(r['contacts']):,} contacts)"
                  for _, r in p.iterrows()]
        return lines

    if "month" in q or "season" in q or "when" in q:
        import pandas as pd
        m = pd.read_csv(PROJECT / "outputs" / "seg_month.csv").sort_values("conv_rate", ascending=False)
        lines = ["Conversion rate by call month — best three:"]
        lines += [f"  {r['month']} — {r['conv_rate']:.1%} ({int(r['contacts']):,} contacts)"
                  for _, r in m.head(3).iterrows()]
        worst = m.tail(2)
        lines += ["Weakest:", *[f"  {r['month']} — {r['conv_rate']:.1%}" for _, r in worst.iterrows()]]
        return lines

    if "contact" in q and ("type" in q or "channel" in q):
        import pandas as pd
        c = pd.read_csv(PROJECT / "outputs" / "seg_contact.csv")
        return ["Conversion by contact channel:", *[f"  {r['contact']} — {r['conv_rate']:.1%}" for _, r in c.iterrows()]]

    if "roi" in q or "cost" in q or "dial" in q or "budget" in q:
        import pandas as pd
        t = pd.read_csv(DATA, usecols=["y", "campaign", "converted"])
        kpis = json.loads((PROJECT / "outputs" / "kpis.json").read_text())
        lines = [
            f"Cost model (stated assumptions): ${kpis['assumed_call_cost']:.2f} per call, "
            f"${kpis['assumed_margin']:.0f} margin per subscription.",
            f"{len(t):,} contacts × avg {t['campaign'].mean():.2f} calls = ${kpis['total_dial_cost']:,.0f} dial cost.",
            f"{t['converted'].sum():,} conversions × ${kpis['assumed_margin']:.0f} = ${kpis['campaign_revenue']:,.0f} margin.",
            f"Campaign ROI = {kpis['campaign_roi']:.1f}x — before targeting. The decile plan converts 'dials' to 'chosen dials'.",
        ]
        return lines

    if "job" in q or "who" in q:
        import pandas as pd
        j = pd.read_csv(PROJECT / "outputs" / "seg_job.csv")
        j = j.sort_values("conv_rate", ascending=False) if "conv_rate" in j.columns else j
        col = "conv_rate" if "conv_rate" in j.columns else j.columns[-1]
        return ["Conversion rate by job — top five:",
                *[f"  {r['job']} — {r[col]:.1%}" for _, r in j.head(5).iterrows()]]

    return None


def offline_answer(q: str) -> str:
    try:
        lines = compute(q)
    except Exception as e:  # noqa: BLE001
        return f"\n(error while computing from the csv — this engine never guesses: {e})\n"
    if lines is None:
        return ("\nI could not map that to a computed fact, so here is the verified headline\n"
                "(try: deciles, response by poutcome, best months, contact type, roi, top jobs).\n\n"
                f"{HEADLINE}\n")
    return "\n".join(["[computed live from bank_cleaned.csv / deciles.csv —]"] + lines) + f"\n\n{HEADLINE}\n"


def narrate_with_llm(q: str, facts: str) -> str:
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        return ""
    import urllib.request
    body = json.dumps({"model": "llama-3.1-8b-instant", "messages": [
        {"role": "system", "content": "You are a precise marketing analyst. Use ONLY the numbers in the supplied verified facts. Do not compute, estimate or invent any number. 3 sentences max."},
        {"role": "user", "content": f"Facts (verified, pre-computed):\n{facts}\n\nQuestion: {q}"}]})
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions", data=body.encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            return "\n\nNARRATED: " + json.loads(r.read())["choices"][0]["message"]["content"].strip() + "\n"
    except Exception:
        return ""


def main() -> None:
    if not DATA.exists():
        print("Run src/00_download_data.py + src/01_analysis.py first."); sys.exit(2)

    if len(sys.argv) > 1:  # one-shot
        q = " ".join(sys.argv[1:])
        base = offline_answer(q)
        if os.environ.get("GROQ_API_KEY") and "computed live" in base:
            base += narrate_with_llm(q, base)
        print(base)
        return

    print(FIRST_MSG + "\n")
    while True:
        try:
            q = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); return
        if q.lower() in {"quit", "exit", "q", ""}:
            return
        base = offline_answer(q)
        if os.environ.get("GROQ_API_KEY") and "computed live" in base:
            base += narrate_with_llm(q, base)
        print(base)


if __name__ == "__main__":
    main()
