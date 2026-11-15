# Rubric — 100 điểm

Điểm dựa trên **bằng chứng trong repo**, không dựa vào việc được Release hay mAP cao. Báo **Hold/Rework** trung thực, có phân tích, vẫn được điểm tốt.

| # | Hạng mục | Điểm | Bằng chứng |
|---|---|---:|---|
| 1 | Bộ check đúng (unit test) | 30 | `pipeline/`, `pytest` |
| 2 | Pipeline tự động hoá một lệnh | 15 | `make run`, `submission/reports/`, test e2e |
| 3 | Calibration | 15 | `submission/calibration/` |
| 4 | Báo cáo lỗi, phân việc, quyết định | 10 | `submission/REPORT.md`, `reports/` |
| 5 | Train so sánh raw vs clean | 15 | `submission/results/` |
| 6 | Phân loại lỗi máy/người, dùng AI có kiểm | 10 | `notes/01_*.md`, `notes/02_*.md` |
| 7 | Tái lập và git | 5 | `check_submission.py`, commit |

## 1. Bộ check đúng (30)
Chấm tự động bằng `pytest` (trên máy chấm, có thêm vài ca ẩn cùng kiểu). Trọng số: `label_format` 6 · `duplicates` 5 · `second_opinion` 6 · `autofix` 5 · `gate` 3 · `images` 2 · `missing_labels` 1 · `class_names` 1 · `stats` 1.
- Trừ: đọc ngưỡng viết cứng trong code thay vì `cfg`; check làm script chết với dòng hỏng; xoá/ghi đè `data/raw`.

## 2. Pipeline tự động hoá (15)
- 5: `make run` chạy từ đầu đến cuối **không cần can thiệp**, mã thoát đúng (0/10/20), ra đủ 8 file báo cáo.
- 4: **Tái lập**: chạy 2 lần cho cùng kết quả (test e2e); không phụ thuộc thứ tự file / thời gian.
- 3: **Cửa chặn thật sự chặn**: lỗi bắt buộc còn lại → Rework, **không xuất** dataset; bạn chứng minh bằng ví dụ (xem `REPORT.md`).
- 3: Mỗi thay đổi tự động có dấu vết (`03_fixes.csv` trước → sau); không sửa `data/raw`.

## 3. Calibration (15)
- 5: chạy sweep cho ≥ 4 tham số; có `calibration_report.md` do script sinh.
- 5: bảng **trước / sau** và **lý do** chọn từng giá trị bằng precision/recall (không chỉ "F1 cao nhất").
- 5: nêu được **một hạn chế/điểm đánh lừa** của calibration (calib nhỏ, phân bố khác, ngưỡng ăn khớp calib nhưng sai trên raw…) có bằng chứng từ chính dữ liệu của bạn.

## 4. Báo cáo lỗi, phân việc, quyết định (10)
- 3: số lỗi theo từng mã (kèm mẫu số), đọc đúng thứ tự "kết luận trước, chi tiết sau".
- 3: **phân việc sửa**: lỗi nào máy sửa, lỗi nào người, ảnh nào ưu tiên; giải thích hàng đợi.
- 4: quyết định Release/Hold/Rework **khớp số liệu**, có điều kiện để đổi quyết định; thừa nhận lỗi pipeline **không** bắt được (đối chiếu `class_stats.csv`, `LOOSE_BOX`…).
- Bị trừ nặng: báo Release trong khi `07_error_list_v3` còn lỗi bắt buộc hoặc cảnh báo ≥ ngưỡng.

## 5. Train so sánh (15)
- 4: đúng quy trình công bằng: cùng val/test/siêu tham số/seed; ≥ 2 seed mỗi biến thể (khuyến nghị 3).
- 4: `comparison.md` do script sinh, đủ mAP50, mAP50-95, precision, recall (TB ± độ lệch).
- 4: `ANALYSIS.md` so sánh chênh lệch với độ nhiễu giữa seed; chỉ ra ≥ 2 nguyên nhân có thể (ảnh trùng/rò rỉ test, box lỏng, thiếu nhãn, lớp ít ảnh…) và cách kiểm.
- 3: kết luận **trung thực** (không nói "tốt hơn" nếu khác biệt nằm trong nhiễu) + việc tiếp theo.

## 6. Phân loại lỗi và dùng AI (10)
- 5: `01_error_taxonomy.md` đầy đủ 22 mã lỗi, ≥ 2 lý do tranh luận có lập luận.
- 5: `02_ai_prompts.md`: ≥ 3 prompt đủ 4 ý, mô tả cách **kiểm** code AI (đọc lướt, chạy trên bản sao, thử trên lỗi biết trước), 1 lần AI sai và bạn phát hiện ra. Không dùng AI → ghi rõ và giải thích một quyết định thiết kế khó.

## 7. Tái lập và git (5)
- 2: `make check` hết LỖI; repo chạy từ `git clone` + `pip install -r requirements.txt`.
- 3: ≥ 6 commit có thông điệp rõ, mang tên bạn; không commit `work/`, `*.pt`.

## Cách chấm trên máy giảng viên
- Ghi đè mọi file "ĐÃ VIẾT SẴN" bằng bản gốc (so `scripts/_protected.json`), giữ `pipeline/checks/*`, `steps/autofix.py`, `steps/gate.py`, `configs/pipeline.yaml` của học viên; chạy `pytest` (có thêm ca ẩn), `make run`, và `check_submission.py`.
- Chấm lại trên lô khác (đổi tên ảnh, xáo trộn vị trí lỗi) để phát hiện code cứng đáp án.
- Số trong báo cáo được đối chiếu với `08_summary.json`, `calibration.json`, `results/*.json` (có `manifest_sha1`, `config_sha1`).

## Thưởng (tối đa +5, không vượt 100)
- +2: thêm một check mới (ví dụ box tiny/dense, lệch tỉ lệ khung hình, class imbalance) có test.
- +2: duyệt tay ≥ 5 ảnh trong CVAT bằng bộ lọc ([docs/CVAT_FILTER.md](docs/CVAT_FILTER.md)), kèm ảnh chụp bộ lọc và so sánh với kết quả pipeline.
- +1: chạy biến thể `oracle` và giải thích khoảng cách `clean` ↔ `oracle`.
