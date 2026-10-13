"""05-marketing-campaign — download UCI Bank Marketing dataset (public).

Source: https://archive.ics.uci.edu/dataset/222/bank+marketing
Direct phone marketing campaigns of a Portuguese bank, ~45k contacts.
"""
from pathlib import Path
import sys

_shared_root = Path(__file__).resolve().parent
while _shared_root != _shared_root.parent and not (_shared_root / "shared").is_dir():
    _shared_root = _shared_root.parent
sys.path.insert(0, str(_shared_root))  # callable from repo root or standalone checkout
from shared.utils import download, unzip   # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent
URL = "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip"


def main() -> None:
    raw = PROJECT / "data" / "raw"
    z = download(URL, raw / "bank_marketing.zip", "UCI Bank Marketing")
    unzip(z, raw)
    inner = raw / "bank.zip"
    if inner.exists():
        unzip(inner, raw)
    print("[done] files:", [p.name for p in sorted(raw.glob("*")) if p.is_file()])


if __name__ == "__main__":
    main()
