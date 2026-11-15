"""CHECK 4b — Ảnh trùng: md5 (trùng từng byte) + perceptual hash (trùng gần đúng) + rò rỉ sang test/val.   (Script 4 trong slide)   ★★

Test:  pytest tests/test_duplicates.py -q

Slide: "md5 bắt file trùng từng byte; bản thu nhỏ cần mã băm theo hình (perceptual hash)".

Duyệt ảnh theo thứ tự tên; ảnh ĐẦU TIÊN được giữ, ảnh sau trùng với nó thì bị báo (`image` = ảnh bị báo).
Mỗi ảnh nhiều nhất một issue, theo thứ tự ưu tiên:

| code            | severity | khi nào                                                                              |
|-----------------|----------|--------------------------------------------------------------------------------------|
| LEAK_TEST       | ERROR    | trùng (md5 hoặc phash <= phash_dist) với ảnh trong `cfg["intake"]["reference_dirs"]` (test/val) |
| DUP_IMAGE_EXACT | ERROR    | cùng md5 với ảnh đã giữ;  extra={"of": tên ảnh gốc}                                  |
| DUP_IMAGE_NEAR  | ERROR    | khác md5 nhưng khoảng cách phash <= `cfg["duplicates"]["phash_dist"]`; extra={"of":..., "dist":...} |

Gợi ý
- `hashlib.md5(path.read_bytes()).hexdigest()`; `imagehash.phash(Image)` — hiệu hai hash = khoảng cách Hamming.
- Đường dẫn `reference_dirs` tính từ `ROOT` (import từ ..common). Ảnh hỏng thì bỏ qua (check `images` đã báo).
- `phash_dist` KHÔNG phải số thần thánh: bạn sẽ calibrate nó ở Pha 4.
- Rò rỉ là lỗi nghiêm trọng nhất: ảnh test lọt vào train làm điểm đánh giá đẹp giả.
"""
import hashlib  # noqa: F401
from pathlib import Path  # noqa: F401

import imagehash  # noqa: F401
from PIL import Image  # noqa: F401

from ..common import ERROR, ROOT, Issue  # noqa: F401


def run(ds, cfg):
    # TODO
    raise NotImplementedError("check duplicates chưa làm")
