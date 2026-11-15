"""CHECK 3 — Tên lớp trong `data.yaml` có đúng danh sách của dự án không?   (Script 3 trong slide)   ★

Test:  pytest tests/test_class_names.py -q

Bắt `Car` (viết hoa), `pedestrian` (đúng ra là `person`), tên đứng sai id, thiếu/thừa lớp.
`extra` (không bắt buộc) nên có {"id": id, "name": tên} khi lỗi gắn với một tên lớp.
Mọi lỗi dùng:  code="BAD_CLASS_NAME", severity=ERROR, image="data.yaml".

Gợi ý
- `ds.yaml_names()` -> {id: tên}. Danh sách đúng: `cfg["classes"]` (vị trí trong list = id).
- Một tên có thể hợp lệ nhưng ĐỨNG SAI id (vd id 0 là `person`): vẫn là lỗi, vì nhãn YOLO chỉ lưu id.
- Không đọc được tên nào (`{}`) cũng là lỗi.
"""
from ..common import ERROR, Issue  # noqa: F401


def run(ds, cfg):
    # TODO
    raise NotImplementedError("check class_names chưa làm")
