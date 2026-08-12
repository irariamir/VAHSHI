#!/usr/bin/env python3
"""Sync counseling clock to Asia/Tehran and write state/clock.json."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    from backports.zoneinfo import ZoneInfo  # type: ignore

try:
    import jdatetime
except ImportError:
    jdatetime = None

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "state" / "clock.json"
FA_WD = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]


def sync(source: str = "system") -> dict:
    now = datetime.now(ZoneInfo("Asia/Tehran"))
    payload = {
        "timezone": "Asia/Tehran",
        "utc_offset": "+03:30",
        "gregorian": now.strftime("%Y-%m-%d"),
        "gregorian_time": now.strftime("%H:%M:%S"),
        "iso": now.isoformat(timespec="seconds"),
        "weekday_en": now.strftime("%A"),
        "source": source,
        "authority": "system",
        "synced_at": now.isoformat(timespec="seconds"),
    }
    if jdatetime is not None:
        j = jdatetime.datetime.fromgregorian(datetime=now)
        payload.update(
            {
                "jalali": j.strftime("%Y/%m/%d"),
                "jalali_time": j.strftime("%H:%M:%S"),
                "weekday_fa": FA_WD[j.weekday()],
                "jalali_year": j.year,
                "jalali_month": j.month,
                "jalali_day": j.day,
            }
        )
    else:
        payload["jalali"] = None
        payload["weekday_fa"] = None
        payload["warning"] = "jdatetime not installed"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload["chat_light"]=True
    payload["chat_rules"]=["no_code","no_paths","no_json","tehran_time_first"]
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # also mirror under data/ if present
    alt = ROOT / "data" / "state" / "clock.json"
    if (ROOT / "data").exists():
        alt.parent.mkdir(parents=True, exist_ok=True)
        alt.write_text(OUT.read_text(encoding="utf-8"), encoding="utf-8")
    return payload


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--source", default="system")
    args = ap.parse_args(argv)
    data = sync(source=args.source)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(
            f"TEHRAN {data.get('jalali')} {data.get('weekday_fa')} "
            f"{data.get('jalali_time')} | {data.get('gregorian')} {data.get('gregorian_time')} (+03:30)"
        )
        print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
