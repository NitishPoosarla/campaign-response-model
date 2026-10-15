"""05 — banner: sage board, decile ladder, dial math."""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

k = json.loads((Path(__file__).resolve().parents[1] / "outputs" / "kpis.json").read_text())

fig, ax = plt.subplots(figsize=(12, 6.75), dpi=100)
ax.set_xlim(0, 12); ax.set_ylim(0, 6.75); ax.axis("off")
fig.patch.set_facecolor("#e7ebdd")

ax.text(0.5, 6.0, "The call list writes itself (if you let a model write it)",
        fontsize=19, fontweight="bold", color="#33402c")
ax.text(0.5, 5.45, "45,211 dials from UCI Bank Marketing, public data — who converts and where the budget goes",
        fontsize=10.5, color="#5d6a52")

# left: headline facts
ax.text(0.5, 4.35, "10%", fontsize=40, fontweight="bold", color="#33734c", va="center")
ax.text(2.75, 4.35, "of contacts → 61% of\nall conversions", fontsize=12.5,
        color="#33402c", va="center", linespacing=1.4)
ax.text(0.5, 3.0, "6.1x", fontsize=40, fontweight="bold", color="#33734c", va="center")
ax.text(2.75, 3.0, "conversion rate vs the\nbaseline on that decile", fontsize=12.5,
        color="#33402c", va="center", linespacing=1.4)

# right: schematic decile ladder (relative sizes, decile 1 emphasized)
heights = [1.0, 0.42, 0.30, 0.24, 0.19, 0.16, 0.13, 0.11, 0.09, 0.07]
for i, h in enumerate(heights):
    ax.add_patch(plt.Rectangle((5.6 + i * 0.62, 1.6), 0.52, 2.9 * h,
                               color="#a9bf7f" if i else "#33734c"))
ax.text(5.6, 4.75, "model deciles · capture of conversions", fontsize=10, color="#5d6a52")

ax.text(0.5, 0.85,
        f"Stated economics: \\${k['assumed_call_cost']:.2f}/dial, \\${k['assumed_margin']:.0f} margin per conversion\n"
        f"→ program ROI {k['campaign_roi']:.1f}x if we call only what the model ranks top-decile-first.",
        fontsize=11, color="#33402c", linespacing=1.4)
fig.savefig(Path(__file__).resolve().parents[1] / "outputs" / "banner.png",
            dpi=100, facecolor=fig.get_facecolor())
print("banner written")
