"""BƯỚC 2/4 — Sửa tự động những lỗi bắt buộc mà máy sửa được AN TOÀN.   ★★

Test:  pytest tests/test_autofix.py -q

`fix(ds, issues, cfg) -> list[dict]`: duyệt `issues` (chỉ lỗi severity ERROR), sửa thẳng vào thư mục `ds`,
và trả về danh sách thay đổi; mỗi phần tử có khoá: image, line, action, before, after
(đây chính là file `03_fixes.csv` — bằng chứng pipeline đã làm gì, người có thể kiểm lại).

| code lỗi                                       | cách sửa                                    | action           |
|------------------------------------------------|---------------------------------------------|------------------|
| BAD_FORMAT, BAD_CLASS_ID, BOX_ZERO, DUP_BOX    | xoá dòng đó khỏi file nhãn                  | "drop_line"      |
| BOX_OUT_OF_IMAGE                               | cắt box về trong [0,1] (giữ nguyên lớp)     | "clip_box"       |
| MISSING_LABEL_FILE                             | KHÔNG sửa file (máy không thể bịa nhãn): ghi 1 dòng fix, before="(không có file)", after="chuyển người gán" | "needs_label" |
| BAD_CLASS_NAME                                 | ghi lại `names` trong data.yaml đúng `cfg["classes"]` | "rename_classes" |
| DUP_IMAGE_*, LEAK_TEST, CORRUPT_IMAGE, BAD_SIZE| xoá ảnh + nhãn khỏi `ds`                    | "remove_image"   |

Bẫy cần nghĩ tới (có test cho từng cái)
- Một file có NHIỀU dòng lỗi: số dòng trong `issues` là số dòng GỐC. Nếu xoá từng dòng một thì số dòng lệch.
  Gom theo file, rồi ghi lại MỘT lần.
- Sau khi cắt, box có thể không còn diện tích (nằm hẳn ngoài ảnh): lúc đó xoá dòng thay vì ghi box rỗng.
- Một dòng có 2 lỗi (vd. BOX_OUT_OF_IMAGE + DUP_BOX): xoá dòng thắng, chỉ ghi 1 fix `drop_line`, không ghi thêm `clip_box`. Dòng trống ở giữa file vẫn đếm vào số dòng gốc.
- Ảnh vừa bị xoá (DUP_IMAGE_*...) mà còn issue dòng của chính nó: bỏ qua êm, không được báo lỗi/chết.
- Không động tới lỗi WARN (cảnh báo là việc của người). Không sửa file ở `data/raw/` — chỉ sửa `ds`.
- Chạy lần 2 trên dữ liệu đã sửa phải không làm gì thêm (idempotent) — NGOẠI LỆ duy nhất: `needs_label` được ghi lại mỗi lần còn lỗi `MISSING_LABEL_FILE` (vì ảnh vẫn chưa có nhãn).

- `needs_label` KHÔNG tạo file nhãn rỗng (rỗng = "ảnh nền", khác với "chưa gán"). `review_queue` sẽ đẩy ảnh này lên đầu hàng đợi cho người.

Gợi ý: `yaml.safe_load / safe_dump`.
"""
from collections import defaultdict  # noqa: F401
from pathlib import Path

import yaml  # noqa: F401

from ..common import ERROR, ROOT, parse_yolo_line  # noqa: F401

DROP_CODES = {"BAD_FORMAT", "BAD_CLASS_ID", "BOX_ZERO", "DUP_BOX"}
CLIP_CODES = {"BOX_OUT_OF_IMAGE"}
REMOVE_CODES = {"DUP_IMAGE_EXACT", "DUP_IMAGE_NEAR", "LEAK_TEST", "CORRUPT_IMAGE", "BAD_SIZE"}


def _fix(image, line, action, before, after):
    return dict(image=image, line=line, action=action, before=before, after=after)


def _guard_not_raw(ds):
    """Không bao giờ được sửa dữ liệu gốc: autofix chỉ làm việc trên bản sao (work/run/ds)."""
    raw = (ROOT / "data" / "raw").resolve()
    root = Path(ds.root).resolve()
    if root == raw or raw in root.parents:
        raise RuntimeError(f"autofix từ chối sửa dữ liệu gốc {root}: chỉ sửa bản sao trong work/")


def _clip(text):
    """Cắt box về [0,1]. Trả dòng mới, hoặc None nếu box không còn diện tích (nằm hẳn ngoài ảnh)."""
    cls, cx, cy, w, h = parse_yolo_line(text)
    x1, x2 = max(0.0, cx - w / 2), min(1.0, cx + w / 2)
    y1, y2 = max(0.0, cy - h / 2), min(1.0, cy + h / 2)
    if x2 - x1 <= 1e-6 or y2 - y1 <= 1e-6:
        return None
    nw, nh = x2 - x1, y2 - y1
    return f"{cls} {x1 + nw / 2:.6f} {y1 + nh / 2:.6f} {nw:.6f} {nh:.6f}"


def _remove_image(ds, stem):
    removed = []
    for p in ds.image_files():
        if p.stem == stem:
            p.unlink()
            removed.append(p.name)
    lp = ds.label_path(stem)
    had_label = lp.exists()
    if had_label:
        lp.unlink()
    ds._size_cache.pop(stem, None)
    return removed, had_label


def _rename_classes(ds, cfg):
    want = dict(enumerate(cfg["classes"]))
    data = {}
    if ds.yaml_path.exists():
        data = yaml.safe_load(ds.yaml_path.read_text(encoding="utf-8")) or {}
    before = data.get("names")
    if isinstance(before, list):
        before_norm = dict(enumerate(before))
    elif isinstance(before, dict):
        before_norm = {int(k): v for k, v in before.items()}
    else:
        before_norm = None
    if before_norm == want:
        return None
    data["names"] = want
    ds.yaml_path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return _fix("data.yaml", None, "rename_classes", str(before), str(want))


def _fix_lines(ds, stem, line_codes):
    """Sửa MỘT file nhãn một lần: `line_codes` = {số dòng gốc: {mã lỗi}}. Xoá thắng cắt."""
    lp = ds.label_path(stem)
    if not lp.exists():
        return []
    raw_lines = lp.read_text(encoding="utf-8", errors="replace").splitlines()
    fixes, out, changed = [], [], False
    for n, text in enumerate(raw_lines, 1):          # đếm cả dòng trống -> khớp số dòng gốc của check
        codes = line_codes.get(n, set())
        if not codes or not text.strip():
            out.append(text)
            continue
        drop = sorted(codes & DROP_CODES)
        if drop:
            fixes.append(_fix(stem, n, "drop_line", text, f"(xoá dòng: {'+'.join(drop)})"))
            changed = True
            continue
        if codes & CLIP_CODES:
            try:
                new = _clip(text)
            except ValueError:
                new = None
            if new is None:
                fixes.append(_fix(stem, n, "drop_line", text, "(xoá dòng: box nằm ngoài ảnh, cắt xong không còn diện tích)"))
            else:
                fixes.append(_fix(stem, n, "clip_box", text, new))
                out.append(new)
            changed = True
            continue
        out.append(text)
    if changed:
        lp.write_bytes("".join(l + "\n" for l in out).encode("utf-8"))     # LF cố định trên mọi OS (tái lập)
    return fixes


def fix(ds, issues, cfg):
    _guard_not_raw(ds)
    errors = [i for i in issues if i.severity == ERROR]
    fixes = []

    # 1) Loại ảnh (trùng / rò rỉ test / hỏng / sai kích thước) — làm trước để bỏ qua issue dòng của ảnh đã xoá.
    removed = set()
    for i in errors:
        if i.code in REMOVE_CODES and i.image not in removed:
            names, had_label = _remove_image(ds, i.image)
            removed.add(i.image)
            if names or had_label:
                fixes.append(_fix(i.image, None, "remove_image", ", ".join(names) or "(chỉ còn nhãn)",
                                  f"(đã xoá ảnh + nhãn: {i.code})"))

    # 2) data.yaml sai tên lớp
    if any(i.code == "BAD_CLASS_NAME" for i in errors):
        f = _rename_classes(ds, cfg)
        if f:
            fixes.append(f)

    # 3) Ảnh chưa có file nhãn: KHÔNG bịa nhãn, KHÔNG tạo file rỗng -> chuyển người gán
    seen_missing = set()
    for i in errors:
        if i.code == "MISSING_LABEL_FILE" and i.image not in removed and i.image not in seen_missing:
            seen_missing.add(i.image)
            if not ds.label_path(i.image).exists():
                fixes.append(_fix(i.image, None, "needs_label", "(không có file)", "chuyển người gán"))

    # 4) Lỗi theo dòng: gom theo file (số dòng là số dòng GỐC), ghi lại mỗi file MỘT lần
    by_file = defaultdict(lambda: defaultdict(set))
    for i in errors:
        if i.code in DROP_CODES | CLIP_CODES and i.line is not None and i.image not in removed:
            by_file[i.image][int(i.line)].add(i.code)
    for stem in sorted(by_file):
        fixes.extend(_fix_lines(ds, stem, by_file[stem]))
    return fixes
