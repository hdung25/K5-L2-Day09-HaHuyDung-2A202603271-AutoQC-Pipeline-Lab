"""CHECK 4a — Cửa vào: ảnh mở được không, đủ độ phân giải không?   (bước 1 của pipeline)   ★

Test:  pytest tests/test_images.py -q

| code          | severity | khi nào                                                    |
|---------------|----------|------------------------------------------------------------|
| CORRUPT_IMAGE | ERROR    | PIL không mở/đọc được ảnh                                  |
| BAD_SIZE      | ERROR    | min(rộng, cao) < `cfg["intake"]["min_side_px"]`; extra={"size": [w, h]} |

Gợi ý
- Ảnh cắt cụt: `Image.open()` KHÔNG ném lỗi, lỗi chỉ lộ khi `im.load()`. Phải gọi `load()` (hoặc `verify()` + `load()`).
- Có file `.jpg` thực ra là rác: `open()` ném `UnidentifiedImageError`.
- Dùng `with Image.open(p) as im:` để không rò file handle.
"""
from ..common import ERROR, Issue  # noqa: F401


def run(ds, cfg):
    # TODO
    raise NotImplementedError("check images chưa làm")
