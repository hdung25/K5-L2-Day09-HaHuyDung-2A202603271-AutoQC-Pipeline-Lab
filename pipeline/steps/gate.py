"""BƯỚC 4 — Cửa chặn: quyết định Release / Hold / Rework.   ★

Test:  pytest tests/test_gate.py -q

Cây quyết định Day 07 (slide Day 09: "Lỗi bắt buộc chặn pipeline; lỗi cảnh báo chuyển người xem"):

  còn ≥ 1 lỗi bắt buộc (severity ERROR)                          -> "Rework"
  không còn lỗi bắt buộc, nhưng tỉ lệ ẢNH còn cảnh báo
      >= cfg["gate"]["warn_ratio_hold"]                          -> "Hold"
  còn lại                                                        -> "Release"

Tỉ lệ cảnh báo = (số ẢNH khác nhau có ≥ 1 cảnh báo) / (tổng số ảnh).  Chú ý:
- chỉ đếm issue có `image` nằm trong `image_stems` (bỏ "<dataset>", "data.yaml");
- bỏ qua ảnh nằm trong `reviewed` (người đã xem, cảnh báo của ảnh đó coi như đã xử lý) — nhưng LỖI BẮT BUỘC thì không bao giờ được bỏ qua;
- mẫu số là số ảnh, không phải số issue.

Trả về dict: decision, n_errors, n_warn_images, n_images, warn_ratio (làm tròn 4 chữ số), reasons (list[str], giải thích bằng tiếng Việt, có số liệu).
"""
from collections import Counter

from ..common import ERROR, WARN  # noqa: F401


def decide(issues, image_stems, cfg, reviewed=frozenset()):
    thr = cfg["gate"]["warn_ratio_hold"]
    stems = set(image_stems)
    reviewed = set(reviewed)
    n_images = len(stems)

    # Lỗi bắt buộc: đếm TẤT CẢ (kể cả cấp dataset như data.yaml, kể cả ảnh đã duyệt) — không gì che được.
    errors = [i for i in issues if i.severity == ERROR]
    # Cảnh báo: chỉ ảnh thuộc dataset và CHƯA được người duyệt; mẫu số là số ảnh.
    warn_images = {i.image for i in issues if i.severity == WARN and i.image in stems and i.image not in reviewed}
    ratio = round(len(warn_images) / n_images, 4) if n_images else 0

    reasons = []
    if errors:
        decision = "Rework"
        by_code = Counter(i.code for i in errors)
        detail = ", ".join(f"{c}×{n}" for c, n in sorted(by_code.items()))
        n_err_img = len({i.image for i in errors})
        reasons.append(f"còn {len(errors)} lỗi bắt buộc trên {n_err_img} ảnh/tệp ({detail}): phải sửa trước khi phát hành")
    elif n_images and ratio >= thr:
        decision = "Hold"
        reasons.append(f"không còn lỗi bắt buộc, nhưng {len(warn_images)}/{n_images} ảnh ({ratio:.1%}) còn cảnh báo chưa người duyệt "
                       f">= ngưỡng {thr:.0%}")
    else:
        decision = "Release"
        reasons.append(f"không còn lỗi bắt buộc; {len(warn_images)}/{n_images} ảnh ({ratio:.1%}) còn cảnh báo chưa duyệt < ngưỡng {thr:.0%}")
    if errors and n_images:
        reasons.append(f"(tham khảo) {len(warn_images)}/{n_images} ảnh ({ratio:.1%}) còn cảnh báo chưa duyệt; ngưỡng Hold {thr:.0%}")
    if reviewed & stems:
        reasons.append(f"{len(reviewed & stems)} ảnh đã được người duyệt (cảnh báo của chúng coi như đã xử lý)")

    return dict(decision=decision, n_errors=len(errors), n_warn_images=len(warn_images), n_images=n_images,
                warn_ratio=ratio, reasons=reasons)
