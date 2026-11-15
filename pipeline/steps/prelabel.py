"""Bước 2 — Pre-label: model (yolo26n) gợi ý nhãn nháp (ĐÃ VIẾT SẴN)."""
from __future__ import annotations

from .. import model_cache


def prelabel_images(ds, stems, cfg) -> list[str]:
    """Ghi file nhãn nháp cho các ảnh trong `stems`. Trả về danh sách stem đã ghi."""
    mc = cfg["models"]["prelabel"]
    sub = type("S", (), {})()                       # Dataset thu nhỏ chỉ gồm các ảnh cần pre-label
    imgs = [p for p in ds.image_files() if p.stem in set(stems)]
    sub.image_files = lambda: imgs
    sub.image_size = ds.image_size
    preds = model_cache.get_preds(sub, cfg, "prelabel")
    ds.labels_dir.mkdir(parents=True, exist_ok=True)
    done = []
    for p in imgs:
        size = ds.image_size(p.stem)
        lines = []
        for c, conf, x, y, w, h in preds.get(p.stem, []):
            if conf < mc.get("conf", 0.25) or (size and w * size[0] * h * size[1] < mc.get("min_area_px", 300)):
                continue
            x1, y1, x2, y2 = max(0, x - w / 2), max(0, y - h / 2), min(1, x + w / 2), min(1, y + h / 2)
            lines.append(f"{int(c)} {(x1 + x2) / 2:.6f} {(y1 + y2) / 2:.6f} {x2 - x1:.6f} {y2 - y1:.6f}")
        ds.label_path(p.stem).write_text("".join(l + "\n" for l in lines), encoding="utf-8")
        done.append(p.stem)
    return done
