"""Test cho check thêm `box_aspect` (thưởng): tỉ lệ khung hình tính theo PIXEL, chỉ cảnh báo, không chết với dòng hỏng."""
from pipeline.checks import box_aspect


def run(make_ds, cfg, lines, size=(640, 480)):
    ds = make_ds(images={"a": 1}, labels={"a": lines}, size=size)
    return box_aspect.run(ds, cfg)


def test_normal_boxes_are_silent(make_ds, cfg):
    assert run(make_ds, cfg, ["1 0.5 0.5 0.1 0.4", "0 0.5 0.5 0.4 0.2"]) == []


def test_thin_tall_box_is_warned_with_line_and_ratio(make_ds, cfg):
    iss = run(make_ds, cfg, ["1 0.5 0.5 0.2 0.3", "1 0.5 0.5 0.02 0.6"])     # 12.8 x 288 px -> 22.5
    assert [(i.code, i.line, i.severity) for i in iss] == [("BOX_ASPECT", 2, "warn")]
    assert abs(iss[0].extra["ratio"] - 22.5) < 0.1 and iss[0].extra["at_edge"] is False


def test_ratio_is_measured_in_pixels_not_normalized_units(make_ds, cfg):
    # w=0.1, h=0.9 chuẩn hoá (9 lần) nhưng ảnh 1280x160: 128 x 144 px -> gần vuông, KHÔNG cảnh báo
    assert run(make_ds, cfg, ["0 0.5 0.5 0.1 0.9"], size=(1280, 160)) == []


def test_wide_flat_box_and_edge_flag(make_ds, cfg):
    iss = run(make_ds, cfg, ["0 0.5 0.995 0.9 0.01"])                       # 576 x 4.8 px, chạm mép dưới
    assert [i.code for i in iss] == ["BOX_ASPECT"] and iss[0].extra["at_edge"] is True


def test_threshold_from_config_and_boundary(make_ds, cfg):
    line = ["1 0.5 0.5 0.05 0.5"]                                            # 32 x 240 px -> 7.5
    assert run(make_ds, cfg, line) == []                                     # mặc định 8: không báo
    cfg["box_aspect"] = {"max_ratio": 7.5}
    assert run(make_ds, cfg, line) == []                                     # đúng bằng ngưỡng: không báo (> chứ không >=)
    cfg["box_aspect"] = {"max_ratio": 5}
    assert [i.line for i in run(make_ds, cfg, line)] == [1]


def test_broken_lines_and_missing_image_do_not_crash(make_ds, cfg):
    ds = make_ds(images={"a": 1}, labels={"a": ["garbage", "93 0.5 0.5 0.01 0.9", "1 0.5 0.5 0 0.5", "", "1 0.5 0.5 0.02 0.6"]})
    assert [(i.code, i.line) for i in box_aspect.run(ds, cfg)] == [("BOX_ASPECT", 5)]   # số dòng gốc giữ nguyên
    ds.image_path("a").unlink()                                              # nhãn mồ côi: không đo được pixel -> bỏ qua
    assert box_aspect.run(ds, cfg) == []
