#!/usr/bin/env python3
"""Kiểm giả thuyết "raw được nhìn trước tập test" (REPORT.md §5, giả thuyết 1).

Chạy SAU `scripts/train_compare.py` (cần các `work/train/runs/<variant>_seed<k>/weights/best.pt`, tức chạy trên Colab
ngay sau notebook). Đánh giá lại MỖI model trên 3 tập con của `data/test`:
  - full    : 100 ảnh test (giống kết quả chính thức)
  - no_leak : bỏ các ảnh test mà pipeline báo LEAK_TEST (đọc từ submission/reports/01_intake.csv, KHÔNG viết cứng)
  - leak    : chỉ các ảnh test bị rò rỉ (ít ảnh => chỉ để nhìn xu hướng, không kết luận)

    python scripts/eval_without_leak.py                 # -> submission/results/leak_check.md|json
    python scripts/eval_without_leak.py --dry-run       # chỉ dựng tập con, không cần ultralytics

Không sửa kết quả chính thức (`*_seed*.json`); chỉ ghi thêm leak_check.*.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = ["car", "person", "truck", "bus"]


def leaked_test_stems(intake_csv: Path) -> list[str]:
    """Tên ảnh test bị rò rỉ sang raw, lấy từ cột extra {"of": "test/test_033.jpg"} của các dòng LEAK_TEST."""
    out = []
    for r in csv.DictReader(open(intake_csv, encoding="utf-8")):
        if r["code"] != "LEAK_TEST" or not r.get("extra"):
            continue
        ref = json.loads(r["extra"]).get("of", "")
        if ref.startswith("test/"):
            out.append(Path(ref).stem)
    return sorted(set(out))


def build_subset(stems: list[str], out: Path) -> Path:
    """Dựng thư mục YOLO chỉ chứa `stems` của data/test; trả về đường dẫn data.yaml (test = val = tập con)."""
    if out.exists():
        shutil.rmtree(out)
    (out / "images").mkdir(parents=True)
    (out / "labels").mkdir()
    src = ROOT / "data" / "test"
    for p in sorted((src / "images").iterdir()):
        if p.stem in stems:
            shutil.copy2(p, out / "images" / p.name)
            lp = src / "labels" / f"{p.stem}.txt"
            if lp.exists():
                shutil.copy2(lp, out / "labels" / lp.name)
    y = out / "data.yaml"
    y.write_text(f"path: {out.resolve()}\ntrain: images\nval: images\ntest: images\nnames:\n"
                 + "".join(f"  {i}: {n}\n" for i, n in enumerate(NAMES)), encoding="utf-8")
    return y


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", default="work/train/runs")
    ap.add_argument("--intake", default="submission/reports/01_intake.csv")
    ap.add_argument("--work", default="work/eval_leak")
    ap.add_argument("--out", default="submission/results")
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--device", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    leak = leaked_test_stems(ROOT / a.intake)
    all_test = sorted(p.stem for p in (ROOT / "data/test/images").iterdir())
    subsets = {"full": all_test, "no_leak": [s for s in all_test if s not in leak], "leak": leak}
    yamls = {k: build_subset(v, ROOT / a.work / k) for k, v in subsets.items()}
    print("ảnh test bị rò rỉ:", leak)
    print({k: len(v) for k, v in subsets.items()})
    if a.dry_run:
        return 0

    from ultralytics import YOLO
    runs = sorted((ROOT / a.runs).glob("*_seed*/weights/best.pt"))
    if not runs:
        sys.exit(f"không thấy best.pt trong {a.runs}: chạy scripts/train_compare.py (notebook ô 6) trước")
    rows = []
    for w in runs:
        name = w.parents[1].name
        variant, seed = name.rsplit("_seed", 1)
        model = YOLO(str(w))
        row = dict(variant=variant, seed=int(seed))
        for k, y in yamls.items():
            kw = dict(data=str(y), split="test", imgsz=a.imgsz, plots=False, verbose=False)
            if a.device is not None:
                kw["device"] = a.device
            m = model.val(**kw)
            row[f"{k}_map50"] = round(float(m.box.map50), 4)
            row[f"{k}_map50_95"] = round(float(m.box.map), 4)
        rows.append(row)
        print("=>", row)

    def mean(v, key):
        xs = [r[key] for r in rows if r["variant"] == v]
        return (round(statistics.mean(xs), 4), round(statistics.stdev(xs), 4) if len(xs) > 1 else 0.0)

    variants = sorted({r["variant"] for r in rows})
    md = ["# Kiểm rò rỉ test (sinh bởi scripts/eval_without_leak.py)", "",
          f"Ảnh test bị rò rỉ sang raw (từ 01_intake.csv, LEAK_TEST): {', '.join(leak)} ({len(leak)}/{len(all_test)} ảnh)", "",
          "| biến thể | mAP50 full | mAP50 no_leak | mAP50 chỉ leak | mAP50-95 full | mAP50-95 no_leak |", "|---|---|---|---|---|---|"]
    for v in variants:
        cells = [mean(v, k) for k in ("full_map50", "no_leak_map50", "leak_map50", "full_map50_95", "no_leak_map50_95")]
        md.append(f"| {v} | " + " | ".join(f"{m:.3f} ± {s:.3f}" for m, s in cells) + " |")
    if {"raw", "clean"} <= set(variants):
        for k in ("full_map50", "no_leak_map50"):
            md.append(f"\nChênh {k} (clean − raw) = **{mean('clean', k)[0] - mean('raw', k)[0]:+.3f}**")
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    (out / "leak_check.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (out / "leak_check.json").write_text(json.dumps(dict(leaked=leak, runs=rows), indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
