# Hướng dẫn làm lab (từng pha)

Bài **cá nhân**, khoảng **8–10 giờ** (đã tính TDD lần đầu và debug) — nên chia **2–3 buổi** (buổi 1: Pha 0–3 đến khi `pytest` xanh; buổi 2: Pha 4–7). Đường tối thiểu ~6 giờ: bỏ phần thưởng, train 2 seed. Các mốc giờ ở CHECKPOINTS là mốc tự kiểm, chậm hơn là bình thường; Colab chạy nền khi bạn viết báo cáo; mốc tự kiểm ở [CHECKPOINTS.md](CHECKPOINTS.md). Lệnh chạy **từ thư mục gốc repo**.
Quy tắc: [RULES.md](RULES.md) · Chấm điểm: [RUBRIC.md](RUBRIC.md) · Nộp: [SUBMISSION.md](SUBMISSION.md).

```
Pha 0  Chuẩn bị + nhìn dữ liệu            (~20')
Pha 1  Phân loại lỗi: máy hay người       (~25')
Pha 2  Viết 6 check cú pháp (TDD)         (~100–120')
Pha 3  Check ngữ nghĩa + autofix + gate   (~90–120')
       Nghỉ                               (10')
Pha 4  Calibration                        (~35')
Pha 5  Chạy pipeline MỘT lệnh, đọc báo cáo (~30')
Pha 6  Train Colab: bấm chạy rồi để nền   (~15' làm; train ~25–40' chạy nền)
Pha 7  Báo cáo (viết trong lúc Colab chạy), kiểm, nộp (~90')
```

## Tóm tắt một trang

| Pha | Việc | Lệnh chính | Sản phẩm |
|---|---|---|---|
| 0 | Cài đặt, xem dữ liệu | `pip install -r requirements.txt`, `python scripts/viz_labels.py img_0001` | — |
| 1 | Phân loại lỗi máy/người | (đọc `data/README.md`) | `notes/01_error_taxonomy.md` |
| 2 | 6 check cú pháp | `pytest tests/test_<tên>.py -q` | `pipeline/checks/*.py` xanh |
| 3 | `second_opinion`, `autofix`, `gate` | `pytest -q` | toàn bộ test xanh |
| 4 | Calibration | `python -m pipeline.calibrate --sweep …` | `calibration/*`, `configs/pipeline.yaml` |
| 5 | Pipeline một lệnh | `make run` | `submission/reports/`, `export/clean_v1/` |
| 6 | Train so sánh | Colab notebook | `submission/results/` |
| 7 | Báo cáo | `make check` | `REPORT.md` |

## Pha 0 — Chuẩn bị

```bash
pip install -r requirements.txt
python -m pytest -q                              # đỏ hết: bình thường, bạn chưa viết gì
python scripts/viz_labels.py img_0001 img_0030   # xem nhãn vẽ lên ảnh -> work/viz/
```
Đọc [data/README.md](data/README.md): lô raw gồm gì, tập test/val/calib để làm gì, **không** có đáp án lỗi của lô raw (bạn phải tự tìm bằng máy).
Mở ≥ 10 ảnh `work/viz/*.png`, ghi lại **3 lỗi bạn tự nhìn thấy bằng mắt** (dùng cho Pha 1).

## Pha 1 — Phân loại lỗi: máy hay người (slide, mục "Máy kiểm quy tắc, người kiểm ý nghĩa")

Điền bảng trong `submission/notes/01_error_taxonomy.md`: với mỗi mã lỗi trong [docs/PIPELINE.md](docs/PIPELINE.md#các-mã-lỗi),
ghi **ai bắt chắc nhất** (máy / người / cả hai), nó thuộc loại nào trong **5 loại lỗi Day 07** (bỏ sót, thừa, sai lớp, sai vị trí/kích thước, sai thuộc tính),
và **lỗi bắt buộc** (chặn pipeline) hay **cảnh báo** (chuyển người). Ghi lý do cho ≥ 2 mã gây tranh luận.

## Pha 2 — Viết 6 check cú pháp (TDD)

Mỗi file trong `pipeline/checks/` là một **stub** có docstring mô tả chính xác đầu vào/đầu ra. Làm theo thứ tự dễ → khó:

| # | File | Test | Slide |
|---|---|---|---|
| 1 | `missing_labels.py` | `tests/test_missing_labels.py` | Script 1 |
| 2 | `class_names.py` | `tests/test_class_names.py` | Script 3 |
| 3 | `images.py` | `tests/test_images.py` | cửa vào |
| 4 | `label_format.py` | `tests/test_label_format.py` | Script 2 |
| 5 | `stats.py` | `tests/test_stats.py` | Script 5 |
| 6 | `duplicates.py` | `tests/test_duplicates.py` | Script 4 |

Vòng lặp mỗi check: đọc docstring → viết → `pytest tests/test_<tên>.py -q` → sửa → commit.
Test cũng là danh sách bẫy từ slide: đuôi `.JPG`, dòng thiếu cột, ảnh cắt cụt, ảnh thu nhỏ 90% mà md5 không bắt được…

> Dùng AI? OK, nhưng theo [docs/PROMPTING.md](docs/PROMPTING.md): mô tả đủ 4 ý, **đọc lướt có xoá/ghi đè file không**, chạy test, và ghi prompt vào `notes/02_ai_prompts.md`.

## Pha 3 — Check ngữ nghĩa, sửa tự động, cửa chặn

1. `checks/second_opinion.py` — so nhãn với **yolo26l** (model lớn hơn). Chỉ **cảnh báo**: thiếu box, sai lớp, box lỏng, box thừa. Dự đoán của model đã được lưu sẵn trong `data/cache/` nên **không cần GPU**.
2. `steps/autofix.py` — sửa an toàn các lỗi bắt buộc và ghi từng thay đổi (`03_fixes.csv`).
3. `steps/gate.py` — cây quyết định Release / Hold / Rework.

Khi `python -m pytest -q` xanh hết (64 test), bạn đã có đủ bộ máy. Thử ngay:
```bash
python -m pipeline.run          # có thể ra Hold: lúc này ngưỡng còn là giá trị khởi đầu chưa calibrate
```

## Pha 4 — Calibration (slide: "Thử script bằng lỗi cố ý chèn vào")

`data/calib/` có 39 ảnh nhãn sạch **đã chèn lỗi cố ý** và `MANIFEST.csv` là đáp án. Đọc [docs/CALIBRATION.md](docs/CALIBRATION.md), rồi:

```bash
python -m pipeline.calibrate                                    # bảng precision/recall/F1 với cấu hình hiện tại
make calibrate     # chạy ĐỦ 5 sweep bên dưới và ghi submission/calibration/ (Windows: copy nguyên lệnh một dòng trong Makefile)
```
Các sweep (xem lệnh một dòng trong [Makefile](Makefile)): `duplicates.phash_dist`, `label_format.overflow_tol`, `second_opinion.conf`, `second_opinion.iou_loose`, `second_opinion.fp_conf`. Muốn thử tuỳ ý: `python -m pipeline.calibrate --sweep "second_opinion.conf=0.5,0.7"`.
Chọn giá trị cho 5 tham số `# <-- CALIBRATE` trong `configs/pipeline.yaml`, rồi viết `submission/calibration/CALIBRATION.md`:
bảng **trước / sau**, vì sao chọn giá trị đó (đánh đổi precision–recall), và **một chỗ calibration có thể đánh lừa bạn**.
> Gợi ý: bộ calib chỉ có 39 ảnh. Sau khi chọn, chạy pipeline và **mở xem** các cặp ảnh bị cho là trùng — số ảnh bị loại có hợp lý không?

## Pha 5 — Chạy pipeline MỘT lệnh

```bash
make run          # = python -m pipeline.run. LƯU Ý: make trả 0 cho cả Release/Hold/Rework (kết luận in ở cuối + trong report); muốn mã thoát thật (CI) chạy `python -m pipeline.run; echo $?` -> 0 Release, 10 Hold, 20 Rework
```
Pipeline làm cả 5 bước và ghi báo cáo vào `submission/reports/`:

| File | Nội dung |
|---|---|
| `01_intake.*` | ảnh bị loại ở cửa vào (hỏng, nhỏ, trùng, rò rỉ test) |
| `02_error_list_v1.*` | **danh sách lỗi TRƯỚC khi sửa** (đây là "báo cáo lỗi" của slide) |
| `03_fixes.csv` | mọi thay đổi do máy tự sửa (trước → sau) |
| `04_error_list_v2.*` | lỗi còn lại sau sửa tự động |
| `05_review_queue.csv` | hàng đợi **người duyệt** (xếp theo ưu tiên) |
| `06_review_log.csv` | ảnh nào đã được duyệt (mô phỏng, ngân sách có hạn) |
| `07_error_list_v3.*` | lỗi sau người duyệt + **kết luận** |
| `03b_fixes_after_review.csv`, `03c_dropped_unlabeled.csv` | (chỉ khi cần) sửa tự động lại sau người duyệt · ảnh bị loại ở thí nghiệm `--drop-unlabeled` |
| `08_summary.json`, `class_stats.csv` | tóm tắt, đếm box theo lớp |

> **Ảnh chưa có file nhãn** (`MISSING_LABEL_FILE`): lô tới tay bạn đã được pre-label bằng yolo26n (giảng viên chạy, bạn **không** chạy model gán nhãn), nhưng vài ảnh bị rơi mất file nhãn. Máy **không bịa nhãn**: `autofix` ghi `needs_label`, `review_queue` đẩy các ảnh này lên **đầu** hàng đợi để người gán. Nếu người chưa kịp gán hết (vd. ngân sách = 0) thì còn lỗi bắt buộc → **Rework**, không xuất.

Đọc báo cáo (kết luận trước, chi tiết sau — như slide). Trong `REPORT.md` ghi: bao nhiêu lỗi mỗi loại, **ai sửa** (máy hay người), quyết định Release/Hold/Rework và vì sao.

Bước **người duyệt** được mô phỏng (`scripts/human_review_sim.py`): ngân sách 80 ảnh đầu hàng đợi được thay bằng nhãn người.
Muốn duyệt bằng tay? `python -m pipeline.run --no-review` (mã thoát 30 = tạm dừng), sửa nhãn vài ảnh đầu hàng đợi ngay trong `work/run/ds/labels/` (hoặc qua CVAT, [docs/CVAT_FILTER.md](docs/CVAT_FILTER.md)), rồi `python -m pipeline.run --resume-after-review`: ảnh nào có nhãn **đổi** (so sánh sha1) mới được tính là đã duyệt, và không được vượt ngân sách 80 ảnh.

## Pha 6 — Train trên Colab: dữ liệu gốc vs dữ liệu sau pipeline

> Kết luận **Rework** (không xuất `clean_v1`) vẫn là kết quả trung thực được điểm. Muốn vẫn train so sánh: `python -m pipeline.run --export-on-rework` xuất bản **NHÁP** (manifest ghi `decision: Rework`) — ghi rõ điều này trong ANALYSIS.md.
> Mỗi lần chạy lại pipeline là sinh lại `export/clean_v1/manifest.json` (không còn ngày tháng, nên cùng cấu hình + dữ liệu cho cùng băm). Nếu bạn đổi config/code **sau** khi train, `make check` báo `manifest_sha1` lệch và bạn phải train lại: hãy chốt pipeline TRƯỚC khi train.

1. `git add submission/export submission/reports && git commit && git push` (đã có `export/clean_v1`).
2. Mở [notebooks/day09_train_compare.ipynb](notebooks/day09_train_compare.ipynb) trên Colab (Runtime → T4 GPU), điền `REPO_URL` là repo **của bạn**.
3. Chạy hết: train `raw` và `clean` (yolo26n, 40 epoch, **3 seed**), cùng tập val (`data/gold_val`, 40 ảnh) và cùng tập **test** (`data/test`, 100 ảnh nhãn người).
4. Tải `submission/results/` về (notebook có ô lưu) và commit. Colab rớt giữa chừng? Chạy lại lệnh train với `--skip-existing`.
   Muốn tách hiệu ứng của 80 ảnh "nhãn người": `make run-auto` (không người duyệt, loại ảnh chưa có nhãn bằng `--drop-unlabeled` → `export/clean_auto`) rồi thêm `auto` vào `VARIANTS` trong notebook.
5. Viết `submission/results/ANALYSIS.md`: bảng, chênh lệch **so với độ lệch giữa các seed**, các yếu tố gây nhiễu (ảnh trùng/rò rỉ test trong `raw`, nhãn lỗi còn lại trong `clean`), và kết luận **trung thực**.

Không có Colab? Chạy cục bộ (`pip install -r requirements-train.txt`): `python scripts/train_compare.py --variants raw clean --seeds 0 1 --epochs 30 --device mps` (hoặc `cpu`, chậm).

## Pha 7 — Báo cáo và nộp

```bash
make check        # python scripts/check_submission.py
```
Sửa hết `LỖI`, đổi dòng tiêu đề README, đối chiếu [SUBMISSION.md](SUBMISSION.md), nộp link repo.

## Lỗi hay gặp

| Triệu chứng | Cách xử lý |
|---|---|
| `NotImplementedError` ở e2e | còn module chưa viết: chạy `pytest -q` xem file nào đỏ |
| `pytest` xanh nhưng `make run` ra nhiều lỗi lạ | test chỉ phủ ca điển hình; mở `02_error_list_v1.txt` đọc vài dòng và so với `viz_labels.py` |
| `make run` báo 0 lỗi | check của bạn quá lỏng, hoặc chạy sai thư mục (slide: "luôn in số ảnh đã quét") |
| Số ảnh bị loại ở bước 1 quá nhiều | `phash_dist` quá lớn → ảnh khác nhau bị coi là trùng |
| Ra Hold dù đã calibrate | ≥ 10% ảnh còn cảnh báo chưa được người duyệt (hàng đợi lớn hơn ngân sách 80): ngưỡng cảnh báo lỏng quá → calibrate lại; nếu hợp lý thì ghi Hold + lý do |
| Colab báo thiếu `manifest.json` | bạn chưa commit/push `submission/export/clean_v1/` |
| `ModuleNotFoundError: imagehash` | `pip install -r requirements.txt` |
