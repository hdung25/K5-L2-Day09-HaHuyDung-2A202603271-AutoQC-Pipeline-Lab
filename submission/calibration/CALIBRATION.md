# Calibration — <Họ và tên>

> Xoá `TODO(học viên)`. Bảng số lấy từ `calibration_report.md` (do script sinh).

## 1. Cấu hình khởi đầu → sau calibrate
| Tham số | Khởi đầu | Đã chọn | Precision / Recall (trước → sau) | Lý do |
|---|---|---|---|---|
| `duplicates.phash_dist` | 2 | TODO(học viên) | | |
| `label_format.overflow_tol` | 0.02 | TODO(học viên) | | |
| `second_opinion.conf` | 0.25 | TODO(học viên) | | |
| `second_opinion.iou_loose` | 0.6 | TODO(học viên) | | |
| `second_opinion.fp_conf` | 0.25 | TODO(học viên) | | |

## 2. Đánh đổi precision / recall
TODO(học viên): với mỗi tham số ở trên, "giá của một FP" và "giá của một FN" trong dự án này là gì? Vì sao chọn điểm đó?

## 3. Một chỗ calibration có thể đánh lừa
TODO(học viên): chọn một: (a) calib nhỏ nên số nhảy; (b) ngưỡng tốt trên calib nhưng sai trên raw — nêu **bằng chứng** (vd. số ảnh bị loại ở bước 1, mở xem vài cặp ảnh "trùng"); (c) loại lỗi không ngưỡng nào bắt được.

## 4. Ảnh hưởng lên pipeline
TODO(học viên): chạy `make run` với cấu hình khởi đầu và cấu hình đã chọn; so kích thước hàng đợi và kết luận (Release/Hold/Rework).
