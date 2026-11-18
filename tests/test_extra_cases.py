"""Ca khó TỰ THÊM (GUIDE.md Bước 2: "test xanh chưa chắc đúng"): dòng dính 2 lỗi, dòng trống giữa file, nhiều dự đoán / ảnh."""
import pytest

from pipeline.checks import label_format
from pipeline.checks import second_opinion as so
from pipeline.common import Issue
from pipeline.steps import autofix, gate


def codes_at(issues, line):
    return sorted(i.code for i in issues if i.line == line)


# ---------------- label_format ----------------
def test_one_line_out_of_image_and_duplicate_reports_both(make_ds, cfg):
    ds = make_ds(images={"a": 1}, labels={"a": ["1 0.95 0.5 0.2 0.2", "1 0.95 0.5 0.2 0.2"]})
    iss = label_format.run(ds, cfg)
    assert codes_at(iss, 1) == ["BOX_OUT_OF_IMAGE"]
    assert codes_at(iss, 2) == ["BOX_OUT_OF_IMAGE", "DUP_BOX"]


def test_broken_line_is_not_used_as_dup_reference(make_ds, cfg):
    # dòng 1 hỏng (id 93) không được làm "bản gốc" để báo DUP_BOX cho dòng 2
    ds = make_ds(images={"a": 1}, labels={"a": ["93 0.5 0.5 0.2 0.3", "1 0.5 0.5 0.2 0.3"]})
    assert codes_at(label_format.run(ds, cfg), 2) == []


def test_orphan_label_without_image_does_not_crash(make_ds, cfg):
    ds = make_ds(images={}, labels={"ghost": ["1 0.5 0.5 0.01 0.3", "7 0.5 0.5 0.2 0.2"]})
    iss = label_format.run(ds, cfg)
    assert [(i.code, i.line) for i in iss] == [("BAD_CLASS_ID", 2)]     # không có ảnh -> không đo được BOX_TINY


def test_uppercase_extension_image_is_measured_for_tiny(make_ds, cfg):
    ds = make_ds(images={"A.JPG": 1}, labels={"A": ["1 0.5 0.5 0.01 0.3"]}, size=(640, 480))
    assert [i.code for i in label_format.run(ds, cfg)] == ["BOX_TINY"]


def test_crlf_and_blank_lines_keep_numbers(make_ds, cfg):
    ds = make_ds(images={"a": 1})
    ds.label_path("a").write_bytes(b"1 0.5 0.5 0.2 0.3\r\n\r\n   \r\n1 0.5 0.5 0.2\r\n")
    assert [(i.code, i.line) for i in label_format.run(ds, cfg)] == [("BAD_FORMAT", 4)]


# ---------------- autofix ----------------
def test_autofix_end_to_end_with_mixed_errors_and_blank_lines(make_ds, cfg):
    lines = ["1 0.5 0.5 0.2 0.2", "", "1 0.95 0.5 0.2 0.2", "93 .5 .5 .2 .2", "1 0.5 0.5 0.2 0.2", "1 -0.3 0.5 0.1 0.1"]
    ds = make_ds(images={"a": 1}, labels={"a": lines})
    fx = autofix.fix(ds, label_format.run(ds, cfg), cfg)
    assert [(f["line"], f["action"]) for f in fx] == [(3, "clip_box"), (4, "drop_line"), (5, "drop_line"), (6, "drop_line")]
    assert label_format.run(ds, cfg) == []                               # sau sửa: sạch
    assert autofix.fix(ds, label_format.run(ds, cfg), cfg) == []         # idempotent


def test_autofix_refuses_to_touch_raw(cfg):
    from pipeline.common import ROOT, Dataset
    ds = Dataset(ROOT / "data" / "raw", cfg["classes"])
    with pytest.raises(RuntimeError):
        autofix.fix(ds, [Issue("x", "error", "BAD_CLASS_ID", "img_0001", "m", 1)], cfg)


def test_autofix_missing_label_logged_each_run_but_no_file(make_ds, cfg):
    ds = make_ds(images={"a": 1})
    iss = [Issue("missing_labels", "error", "MISSING_LABEL_FILE", "a", "m")]
    assert [f["action"] for f in autofix.fix(ds, iss, cfg)] == ["needs_label"]
    assert [f["action"] for f in autofix.fix(ds, iss, cfg)] == ["needs_label"]
    assert not ds.label_path("a").exists()


# ---------------- second_opinion ----------------
def test_many_predictions_one_image(make_ds, cfg):
    labels = ["0 0.5 0.5 0.3 0.4", "2 0.15 0.3 0.12 0.3", "1 0.9 0.9 0.05 0.05"]
    preds = [[0, 0.9, 0.5, 0.5, 0.3, 0.4],          # khớp dòng 1: im lặng
             [0, 0.9, 0.15, 0.3, 0.12, 0.3],        # dòng 2 gán truck, model nói car -> WRONG_CLASS
             [1, 0.9, 0.8, 0.2, 0.12, 0.3],         # không nhãn -> MISSING
             [1, 0.2, 0.8, 0.2, 0.12, 0.3],         # conf thấp -> bỏ (MISSING), nhưng vẫn không cứu dòng 3
             [0, 0.9, 0.5, 0.5, 0.45, 0.55]]        # cùng vật dòng 1, box to hơn: IoU ≈ 0.48 < iou_loose 0.6 -> LOOSE_BOX
    ds = make_ds(images={"a": 1}, labels={"a": labels}, size=(640, 480))
    got = [(i.code, i.line) for i in so.run(ds, cfg, preds={"a": preds})]
    assert got == [("POSSIBLE_WRONG_CLASS", None), ("POSSIBLE_MISSING", None), ("POSSIBLE_LOOSE_BOX", None), ("POSSIBLE_FALSE_POS", 3)]


def test_image_with_empty_prediction_list_flags_all_labels_as_false_pos(make_ds, cfg):
    ds = make_ds(images={"a": 1}, labels={"a": ["0 0.5 0.5 0.3 0.4", "", "1 0.1 0.1 0.1 0.1"]})
    assert [(i.code, i.line) for i in so.run(ds, cfg, preds={"a": []})] == [("POSSIBLE_FALSE_POS", 1), ("POSSIBLE_FALSE_POS", 3)]


def test_warnings_carry_conf_for_queue_priority(make_ds, cfg):
    ds = make_ds(images={"a": 1}, labels={"a": ["0 0.5 0.5 0.3 0.4"]})
    iss = so.run(ds, cfg, preds={"a": [[0, 0.9, 0.5, 0.5, 0.3, 0.4], [1, 0.77, 0.15, 0.3, 0.12, 0.3]]})
    assert [i.extra["conf"] for i in iss] == [0.77]


# ---------------- gate ----------------
def test_gate_dataset_level_error_still_reworks(cfg):
    d = gate.decide([Issue("class_names", "error", "BAD_CLASS_NAME", "data.yaml", "m")], ["a", "b"], cfg)
    assert d["decision"] == "Rework" and d["n_errors"] == 1
