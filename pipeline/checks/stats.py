"""CHECK 5 — Đếm box theo lớp để thấy bất thường.   (Script 5 trong slide)   ★

Test:  pytest tests/test_stats.py -q

Cần hai hàm:

1. `class_counts(ds) -> collections.Counter`: đếm số box theo TOKEN ĐẦU DÒNG (chuỗi, ví dụ "1", "93").
   Dùng token chứ không ép int: id lạ như `93` hay `-1` phải hiện ra trong bảng đếm.
   Bỏ qua dòng trống. (Hàm này còn được `pipeline/run.py` gọi để ghi `class_stats.csv`.)

2. `run(ds, cfg)` -> list[Issue], đều severity WARN:

| code        | image      | khi nào                                                               |
|-------------|------------|-----------------------------------------------------------------------|
| CLASS_RARE  | "<dataset>"| token lớp có < `cfg["stats"]["rare_class_min_boxes"]` box; `extra={"class": token, "n": số box}` |
| DENSE_IMAGE | stem       | ảnh có > `cfg["stats"]["dense_image_max_boxes"]` box; `extra={"n": số box}` |

"Lớp 93 chỉ có 1 box: ID đáng ngờ, kiểm ngay."
"""
from collections import Counter  # noqa: F401

from ..common import WARN, Issue  # noqa: F401


def class_counts(ds) -> Counter:
    # TODO
    raise NotImplementedError("stats.class_counts chưa làm")


def run(ds, cfg):
    # TODO
    raise NotImplementedError("check stats chưa làm")
