# Báo cáo Day 09 — Hà Huy Dũng, 2A202603271

> Mọi số liệu lấy từ `submission/reports/` (lần chạy `python -m pipeline.run` với `configs/pipeline.yaml` đã calibrate, `config_sha1 = 58d1755c…`), `submission/calibration/` và các lệnh kiểm chứng ghi kèm. Pipeline chạy 2 lần cho **kết quả giống hệt từng byte** (01–07, `class_stats.csv`, nhãn export).

## 1. Kết luận trước

**Pipeline kết luận: HOLD** (mã thoát 10). **224 ảnh vào → 202 ảnh qua cửa vào → 202 ảnh trong bản xuất `submission/export/clean_v1/`** (bản NHÁP, `manifest.json` ghi `decision = Hold`, **chưa phải bản phát hành**).

- **Không còn lỗi bắt buộc nào** (`07_error_list_v3`: 0 error): 22 ảnh hỏng/nhỏ/trùng/rò rỉ test bị loại ở bước 1, 28 dòng nhãn hỏng được máy sửa có log, 6 ảnh thiếu file nhãn đã được người gán.
- Nhưng **38/202 ảnh (18,8 %) còn cảnh báo ngữ nghĩa chưa người duyệt ≥ ngưỡng 10 %**: hàng đợi người duyệt có **125 ảnh** mà ngân sách chỉ **80 ảnh**, 45 ảnh cuối hàng không ai xem.
- Lý do chính: model kiểm (yolo26l) nghi ngờ nhiều lỗi ngữ nghĩa (thiếu box, nhầm lớp, box lỏng) hơn sức duyệt của một vòng; không thể Release khi gần 1/5 lô chưa qua mắt người.

## 2. Lỗi và phân việc

Từ `02_error_list_v1` (TRƯỚC khi sửa; gồm cả lỗi cửa vào ở `01_intake`). Mẫu số: **224 ảnh quét** ở bước 1, **202 ảnh** từ bước QC trở đi.

| Mã lỗi | Số dòng / ảnh | Ai sửa | Vì sao |
|---|---:|---|---|
| `CORRUPT_IMAGE` | 2 ảnh /224 | **máy** (loại ảnh) | ảnh cắt cụt chỉ lộ lỗi khi `load()`; không train được |
| `BAD_SIZE` | 3 ảnh /224 | **máy** (loại) | cạnh ngắn 180–226 px < 250 px (quy tắc dự án) |
| `DUP_IMAGE_EXACT` | 8 ảnh /224 | **máy** (loại) | md5 trùng, giữ bản đầu tiên |
| `DUP_IMAGE_NEAR` | 4 ảnh /224 | **máy** (loại) | phash ≤ 12 (khoảng cách 0, 0, 6, 10) |
| `LEAK_TEST` | 5 ảnh /224 | **máy** (loại) | trùng ảnh `data/test` (4 trùng byte/phash ≤ 2, 1 ảnh có viền đen phash 6) → nếu giữ sẽ thổi phồng mAP test |
| `BAD_CLASS_NAME` | 2 tên / 1 `data.yaml` | **máy** (`rename_classes`) | `Person`, `Bus` → ghi lại đúng `cfg.classes` |
| `BAD_FORMAT` | 3 dòng / 3 ảnh | **máy** (`drop_line`) | 2 dòng `nan`, 1 dòng 4 cột: không suy ra được giá trị đúng |
| `BAD_CLASS_ID` | 6 dòng / 6 ảnh | **máy** (`drop_line`) | id 93, 7, 4, −1: không biết lớp đúng ⇒ xoá, ảnh được đưa vào hàng đợi (`FIXED_DROP_LINE`) |
| `BOX_ZERO` | 4 dòng / 4 ảnh | **máy** (`drop_line`) | w hoặc h = 0 |
| `DUP_BOX` | 7 dòng / 7 ảnh | **máy** (`drop_line`) | cùng lớp, IoU > 0,9 với dòng trước |
| `BOX_OUT_OF_IMAGE` | 8 dòng / 8 ảnh | **máy** (`clip_box`) | tràn 0,023–0,06 ⇒ cắt về [0,1], giữ lớp |
| `MISSING_LABEL_FILE` | 6 ảnh /202 | **người** (`needs_label`) | máy không bịa nhãn, không tạo file rỗng ⇒ ưu tiên 10 trong hàng đợi |
| `POSSIBLE_MISSING` | 53 / 52 ảnh | **người** | model thấy vật (conf ≥ 0,6, ≥ 600 px²) mà nhãn không có box |
| `POSSIBLE_WRONG_CLASS` | 18 / 18 ảnh | **người** | model và nhãn khác lớp trên cùng vật (IoU ≥ 0,5) |
| `POSSIBLE_LOOSE_BOX` | 28 / 24 ảnh | **người** | cùng lớp nhưng IoU < 0,5 |
| `POSSIBLE_FALSE_POS` | 29 / 27 ảnh | **người** | box nhãn không khớp dự đoán nào (conf ≥ 0,1) |
| `EMPTY_LABEL` | 12 ảnh | **người** | rỗng = ảnh nền hay thiếu nhãn? chỉ người phân biệt được |
| `BOX_TINY` / `BOX_HUGE` | 6 / 3 dòng | **người** | quy tắc dự án, chỉ cảnh báo |
| `CLASS_RARE` | 4 (cấp dataset) | — | các token `93, 7, 4, -1` chỉ có 1 box: chính là các ID sai, biến mất sau sửa |

**Tổng: máy xử lý 22 ảnh ở cửa vào + 35 thay đổi trong `03_fixes.csv`** (20 `drop_line`, 8 `clip_box`, 1 `rename_classes`, 6 `needs_label`); mỗi dòng có `before → after` để người kiểm lại. `data/raw` không bị đụng (autofix có chốt chặn từ chối sửa thư mục này, có test).

**Tác dụng phụ đã thấy của autofix** (`04_error_list_v2`): `EMPTY_LABEL` tăng 12 → 15 vì 3 file chỉ có đúng 1 dòng và dòng đó hỏng (`img_0050` w = 0, `img_0104` id 7, `img_0194` id 4), xoá xong thành rỗng — máy không biết đó là ảnh nền hay thiếu nhãn nên vẫn để người xem; `BOX_TINY` tăng 6 → 7 vì `img_0030` dòng 9 sau khi cắt chỉ còn rộng 0,015. Đây là lý do mọi ảnh có `drop_line/clip_box` đều được cộng điểm vào hàng đợi.

**Vì sao `05_review_queue.csv` xếp như vậy?** Điểm = Σ trọng số mã × (1 + conf của model). Đầu hàng là `img_0020` (11,5: vừa bị xoá dòng id 93, vừa bị nghi gán *truck* cho xe buýt, vừa thiếu người), rồi 6 ảnh `NEEDS_LABEL` (10,0) — không gán thì chắc chắn Rework; tiếp theo là ảnh có `WRONG_CLASS` (trọng số 3) và `MISSING` (2) với conf cao. Đuôi hàng là `LOOSE_BOX` (1,5), `BOX_TINY`/`BOX_HUGE` (0,3–0,5).
**Với ngân sách 80 ảnh:** người xem được **toàn bộ 18/18 ảnh `WRONG_CLASS`, 50/52 ảnh `MISSING`, 6/6 ảnh chưa có nhãn**, nhưng chỉ **8/24 ảnh `LOOSE_BOX`** và 12/23 ảnh `FALSE_POS`. Điểm cắt ở ảnh thứ 80 (3,343) và 81 (3,333) nằm giữa một dãy ảnh chỉ có 1 cờ `MISSING` — ranh giới ngân sách là tuỳ ý ở đó.

## 3. Calibration (2 ngưỡng)

`make calibrate` (39 ảnh calib, lỗi chèn có đáp án) → `submission/calibration/calibration_report.md`. Số dưới là precision / recall trên calib.

| Tham số | Khởi đầu | Đã chọn | Precision / Recall (trước → sau) | Lý do (đánh đổi) |
|---|---|---|---|---|
| `duplicates.phash_dist` | 2 | **12** | `DUP_IMAGE_NEAR` 1,00/0,50 → **1,00/0,67**; `EXACT` 1,00/1,00 giữ nguyên | Đây là lỗi **máy tự loại ảnh**, FP = xoá nhầm ảnh tốt ⇒ ưu tiên precision. Trên raw, khoảng cách tới láng giềng gần nhất có **khe trống 10 → 16**: các cặp trùng thật ở 0/2/6/10, không có cặp nào ở 11–15, các cặp *khác hẳn nhau* bắt đầu từ 16. 12 nằm giữa khe (cách ca trùng thật xa nhất 2 bit, cách ảnh khác nhau 4 bit). Raw: 10, 12, 14 đều loại đúng 17 ảnh (ổn định). |
| `second_opinion.conf` | 0,25 | **0,6** | `WRONG_CLASS` 0,56/0,83 → **0,62/0,83**; `MISSING` 0,50/1,00 → **0,57/1,00**; `LOOSE_BOX` 0,29/0,40 → **0,20/0,20**; `FALSE_POS` 0,31/1,00 không đổi (dùng `fp_conf`) | Đây là **cảnh báo cho người**, FN = lỗi lọt vào dataset ⇒ giữ recall của 2 mã quan trọng nhất (WRONG_CLASS trọng số 3, MISSING 2), tăng precision để bớt việc vô ích: 0,6 là conf **cao nhất** mà MISSING còn recall 1,00 (0,7 mất 1/8, 0,8 mất 2/8). Trên raw: cảnh báo v1 271 → 153, hàng đợi 143 → 125. Cái giá: LOOSE_BOX mất 1/5 lỗi chèn (0,40 → 0,20); chấp nhận vì box lỏng ít hại hơn box thiếu/sai lớp, và hạ conf về 0,1 để cứu LOOSE (0,60) thì MISSING precision rơi về 0,40. |

**Không chọn `conf = 0,8` dù nó cho Release.** Tôi đã thử cả lô raw: 0,25 → Hold 28,7 %; 0,6 → Hold 18,8 %; 0,7 → Hold 14,4 %; **0,8 → Release 7,9 %**. Nhưng trên calib, 0,8 làm recall `MISSING` rơi 1,00 → 0,75: hàng đợi nhỏ đi vì checker *mù* hơn, không phải vì dữ liệu sạch hơn. Chọn ngưỡng theo kết luận gate là "Release giả".

**Một chỗ calibration đánh lừa: `phash_dist`.** Bảng sweep calib báo `DUP_IMAGE_NEAR` precision **1,00 ở mọi giá trị** và F1 tốt nhất ở **16** (0,91), thậm chí ở 20 precision vẫn 1,00. Trên raw thì khác hẳn (đếm bằng `checks.duplicates` trên `data/raw`):

| `phash_dist` | 2 | 6 | 10–14 | **16** | **20** |
|---|---:|---:|---:|---:|---:|
| ảnh raw bị loại vì trùng/rò rỉ | 14 | 16 | 17 | **26** | **134** |

Ở 16, 9 ảnh bị loại thêm; tôi mở xem (`submission/figures/phash_pairs.jpg`): **img_0008 (trượt tuyết) vs img_0011 (tennis), img_0113 (người ngồi bàn) vs img_0177 (lướt sóng), img_0013 (bàn laptop) vs test_087 (bóng chày), img_0038 (lướt sóng) vs test_002 (bánh cưới)** đều ở khoảng cách 16 mà hoàn toàn khác nhau; chỉ img_0074/img_0084 là trùng thật (ảnh cắt). Ở 20, 134/224 ảnh bị loại (105 bị gán nhầm `LEAK_TEST`). Calib không thấy vì: (1) chỉ 39 ảnh, 6 ca gần trùng, mỗi ca = 17 % recall; (2) ảnh gán nhầm bị xếp vào `LEAK_TEST` — mã **không có trong đáp án calib** (CALIBRATION.md: calib không có ca LEAK_TEST), nên FP không được đếm. Ở 2 (giá trị khởi đầu) thì ngược lại: lọt `img_0101` (bản có viền đen của `test_039`) vào train — rò rỉ test.

## 4. Cửa chặn và điều pipeline KHÔNG bắt được

**(a) Gate chặn thật.** `python -m pipeline.run --budget 0 --reports work/rep_nb --export-dir work/exp_nb` (không có người duyệt): kết luận **REWORK**, `echo $?` → **20**, log `Bước 5/5 KHÔNG xuất: còn lỗi bắt buộc (Rework)`, thư mục `work/exp_nb` **không được tạo**. Lý do: `còn 6 lỗi bắt buộc trên 6 ảnh (MISSING_LABEL_FILE×6)` (`img_0031, img_0053, img_0126, img_0135, img_0170, img_0219`) — autofix chỉ ghi `needs_label`, không tạo nhãn. Gate đếm **mọi** lỗi ERROR, kể cả lỗi cấp `data.yaml` và lỗi trên ảnh đã duyệt (có test). Ở lần chạy chính, người duyệt gán 6 ảnh này nên lỗi bắt buộc về 0 và kết luận chuyển sang Hold — đúng thứ tự Rework > Hold > Release.

**(b) Điểm mù (có bằng chứng).**
1. **Model kiểm nhầm cùng kiểu với nhãn.** Calib `calib_009` dòng 6: vật thật là *truck*, nhãn chèn *bus*, yolo26l lại nói *car* (conf 0,72) và có sẵn một nhãn *car* chồng lên (IoU 0,95) ⇒ quy tắc "nhãn cùng lớp đã phủ vật" khiến checker im lặng: `WRONG_CLASS` recall chỉ 5/6. Nhầm car↔truck↔bus là lỗi tự nhiên chính của raw, đúng chỗ model cũng yếu.
2. **Box lỏng không bắt được khi model không chắc.** `LOOSE_BOX` recall 1/5 trên calib: 3 box phóng ×1,45–1,58 có dự đoán model với conf chỉ 0,15–0,29 (< 0,6), 1 box không có dự đoán nào. Trên raw, `LOOSE_BOX` cũng là mã bị bỏ lại nhiều nhất (16/24 ảnh ngoài ngân sách).
3. **Ảnh trùng biến đổi mạnh nằm lẫn trong vùng ảnh khác nhau.** `img_0074`/`img_0084` (cắt) có phash 16 — bằng đúng khoảng cách của các cặp hoàn toàn khác nhau, nên **không ngưỡng phash nào** tách được; tương tự calib_037 (16) và calib_038 (18). Cặp này còn trong bộ xuất.
4. **Checker báo động giả nhiều với `FALSE_POS`.** Trong 80 ảnh đã duyệt, nhãn được thay bằng nhãn người, vậy mà **10/12 ảnh từng bị cờ `FALSE_POS` vẫn bị cờ** (và 25/74 ảnh có cờ `second_opinion` vẫn còn cờ) ⇒ các cờ đó là model bỏ sót vật nhỏ/khuất chứ không phải nhãn sai. Mặt trái: 11 ảnh `FALSE_POS` chưa duyệt khiến Hold có thể "oan" một phần.
5. **Cảnh đông.** `img_0160` (bãi đỗ hàng trăm xe tải) chỉ có 4 box; model chỉ cờ vài vật đủ lớn và `DENSE_IMAGE` không kích hoạt vì ít box ⇒ ảnh thiếu nhãn hàng loạt vẫn trông "ít lỗi".
6. **`EMPTY_LABEL` không phân biệt ảnh nền.** `img_0129` (ghế băng, không xe/người) là ảnh nền đúng nhưng vẫn bị cờ; `img_0004` (rỗng) thì thật sự thiếu 2 xe.

**3 lỗi tôi tự nhìn thấy trên ảnh** (`scripts/viz_labels.py`, `submission/figures/viz_flagged.jpg`): `img_0001` thiếu box người lính bên phải; `img_0020` xe buýt bị gán *truck*; `img_0070` người phụ nữ bên trái bị gán *car*; ngoài ra `img_0177` có box *bus* giữa sóng biển. Cả 4 đều đã được máy cờ đúng mã (`MISSING`, `WRONG_CLASS`, `WRONG_CLASS`, `FALSE_POS`).

## 5. Train: raw vs clean (tùy chọn, chấm riêng)

**Chưa chạy** tại thời điểm viết báo cáo: phần train cần GPU (Colab T4), sẽ chạy sau theo `notebooks/day09_train_compare.ipynb` (yolo26n, 20 epoch, seed 0 và 1, cùng val `gold_val` 40 ảnh và test 100 ảnh). Khi có `submission/results/comparison.md` sẽ dán bảng vào đây.

Giả thuyết đặt trước (để kiểm khi có số): (1) `raw` có **5 ảnh trùng test** (`LEAK_TEST`) + 12 ảnh trùng nội bộ ⇒ mAP test của `raw` có thể bị thổi phồng; kiểm bằng cách so AP trên 5 ảnh test bị rò rỉ vs 95 ảnh còn lại. (2) `clean` còn 38 ảnh có cảnh báo chưa duyệt (chủ yếu box lỏng) ⇒ chênh lệch có thể nhỏ; nếu |Δ mAP50| không lớn hơn độ lệch giữa 2 seed thì kết luận là **chưa phân biệt được**, không nói "tốt hơn".

## 6. Quyết định và ghi chú AI

**(a) Quyết định cuối: HOLD** — dataset `clean_v1` không có lỗi bắt buộc nhưng chưa được phát hành. Để thành **Release** cần đưa tỉ lệ ảnh còn cảnh báo chưa duyệt xuống < 10 %, tức ≤ 20/202 ảnh: **duyệt thêm ít nhất 18 trong 38 ảnh còn cảnh báo** (ưu tiên 11 ảnh `FALSE_POS` và 16 ảnh `LOOSE_BOX` ở đuôi `05_review_queue.csv`), hoặc tăng ngân sách vòng duyệt lên ~100 ảnh. Không hạ `second_opinion.conf` để "lách" gate (mục 3). Nếu một vòng duyệt sau để lại lỗi bắt buộc (nhãn mới hỏng), pipeline tự sửa lại một vòng (`03b_fixes_after_review.csv`) và gate vẫn chặn nếu còn.

**(b) Ghi chú AI.** Có dùng AI (Claude Code) để viết 4 module và phân tích.
- *Prompt chính:* "đọc docstring + test của từng stub, viết đúng đặc tả, không đọc đáp án, không sửa file đã ghim, ngưỡng lấy từ `cfg`".
- *Cách kiểm:* chạy `pytest` sau từng module (79/79 xanh), tự viết thêm 12 ca khó trong `tests/test_extra_cases.py` (dòng dính 2 lỗi, dòng trống/CRLF, nhiều dự đoán/ảnh, chặn sửa `data/raw`), chạy pipeline 2 lần so byte, mở ảnh bằng `viz_labels.py`, đọc lướt diff xem có xoá/ghi đè file nào ngoài `ds`.
- *Một lần AI sai:* (1) trong ca test tự viết, AI kỳ vọng một dự đoán cùng lớp với IoU ≈ 0,48 là "im lặng", nhưng theo đặc tả (< `iou_loose` 0,6 trong cấu hình test) phải là `POSSIBLE_LOOSE_BOX` — sửa test, không sửa code; (2) khi phân tích calibration, AI ban đầu khẳng định `conf = 0,6` "không mất recall ở mã nào", đối chiếu bảng sweep thì `LOOSE_BOX` rơi 0,40 → 0,20 — đã ghi rõ đánh đổi này ở mục 3.

*(Thưởng CVAT: không làm.)*
