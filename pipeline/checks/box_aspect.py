"""CHECK THÊM (thưởng) — box có tỉ lệ khung hình bất thường (dải mảnh).   Test: pytest tests/test_box_aspect.py -q

Tỉ lệ tính bằng PIXEL (không phải toạ độ chuẩn hoá): r = max(W/H, H/W) với W = w*rộng_ảnh, H = h*cao_ảnh.
r > `max_ratio` => WARN `BOX_ASPECT` (chỉ cảnh báo: vật bị cắt ở mép ảnh / bị che có thể hợp lệ, người quyết định).
`extra` = {ratio, w_px, h_px, at_edge}; `at_edge` = box chạm mép ảnh (thường là vật bị cắt, hoặc box vừa bị autofix cắt).

Vì sao max_ratio = 8: trên nhãn NGƯỜI của tập val, 99/100 box có r <= 6.6 và chỉ 1/158 box vượt 8 (xe bị che gần hết);
trên lô raw sau autofix có 3/650 box vượt 8, cả 3 là dải người mảnh ở mép ảnh (một box do chính clip_box tạo ra).
Ngưỡng đọc từ `cfg["box_aspect"]["max_ratio"]` nếu có; mặc định DEFAULT_MAX_RATIO (configs/pipeline.yaml đã ghim, không thêm khoá được).

Không nằm trong `checks.QC_CHECKS` (file đăng ký đã ghim). Chạy riêng:
    python -m pipeline.checks.box_aspect work/run/ds --out submission/reports/extra_box_aspect.csv
"""
from __future__ import annotations

from ..common import WARN, Issue, parse_yolo_line

CHECK = "box_aspect"
DEFAULT_MAX_RATIO = 8.0
EDGE_EPS = 0.002


def run(ds, cfg):
    max_ratio = float((cfg.get("box_aspect") or {}).get("max_ratio", DEFAULT_MAX_RATIO))
    issues = []
    for lf in ds.label_files():
        stem = lf.stem
        size = ds.image_size(stem) if ds.image_path(stem) else None
        if not size:
            continue                                   # không đo được pixel: ảnh thiếu/hỏng (check khác báo)
        W, H = size
        for ln, text in ds.read_label_lines(stem) or []:
            try:
                cls, cx, cy, w, h = parse_yolo_line(text)
            except ValueError:
                continue                               # label_format báo BAD_FORMAT
            if not 0 <= cls < len(ds.classes) or w <= 0 or h <= 0:
                continue                               # label_format báo BAD_CLASS_ID / BOX_ZERO
            wp, hp = w * W, h * H
            r = max(wp / hp, hp / wp)
            if r > max_ratio:
                at_edge = (cx - w / 2 <= EDGE_EPS or cy - h / 2 <= EDGE_EPS or cx + w / 2 >= 1 - EDGE_EPS or cy + h / 2 >= 1 - EDGE_EPS)
                issues.append(Issue(CHECK, WARN, "BOX_ASPECT", stem,
                                    f"dòng {ln}: box {ds.classes[cls]} {wp:.0f}x{hp:.0f}px, tỉ lệ {r:.1f} > {max_ratio:g}"
                                    + (" (chạm mép ảnh)" if at_edge else ""), ln,
                                    {"ratio": round(r, 2), "w_px": round(wp, 1), "h_px": round(hp, 1), "at_edge": at_edge}))
    return issues


if __name__ == "__main__":
    import argparse

    from ..common import ROOT, Dataset, load_config, write_issues_csv

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dataset", nargs="?", default="work/run/ds")
    ap.add_argument("--config", default="configs/pipeline.yaml")
    ap.add_argument("--out", help="ghi CSV các cảnh báo")
    a = ap.parse_args()
    cfg = load_config(ROOT / a.config)
    ds = Dataset(ROOT / a.dataset, cfg["classes"])
    iss = run(ds, cfg)
    print(f"đã quét {len(ds.label_files())} file nhãn: {len(iss)} cảnh báo BOX_ASPECT")
    for i in iss:
        print(f"  {i.image}:{i.line}  {i.message}")
    if a.out:
        write_issues_csv(iss, ROOT / a.out)
