"""CHECK 1 — Ảnh nào thiếu file nhãn?   (Script 1 trong slide)   ★ dễ

Test:  pytest tests/test_missing_labels.py -q

Việc cần làm: hoàn thành `run`. Trả về list[Issue] với các mã:

| code                | severity | khi nào                                              | image  |
|---------------------|----------|------------------------------------------------------|--------|
| MISSING_LABEL_FILE  | ERROR    | có ảnh nhưng KHÔNG có `labels/<stem>.txt`            | stem   |
| ORPHAN_LABEL        | WARN     | có file nhãn nhưng không có ảnh                      | stem   |
| EMPTY_LABEL         | WARN     | có file nhãn nhưng rỗng (ảnh nền? hay bị thiếu nhãn?) | stem   |

Gợi ý
- `ds.image_files()` đã xử lý đuôi .JPG/.png; `ds.label_files()`; `ds.read_label_lines(stem)` (None nếu không có file).
- So sánh hai tập tên (stem) như slide: `anh - nhan`, `nhan - anh`.
- Duyệt theo thứ tự đã sắp xếp để báo cáo lần nào cũng giống nhau (tái lập được).
"""
from ..common import ERROR, WARN, Issue  # noqa: F401


def run(ds, cfg):
    # TODO: viết code ở đây
    raise NotImplementedError("check missing_labels chưa làm")
