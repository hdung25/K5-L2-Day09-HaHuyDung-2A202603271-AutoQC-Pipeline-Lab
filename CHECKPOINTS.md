# Checkpoints — Day 09

Bài cá nhân, dự kiến **8–10 giờ (2–3 buổi)**, đường tối thiểu ~6 giờ; Colab chạy nền. Mốc tính từ lúc bắt đầu, là điểm **tự kiểm tra**, không phải hạn nộp.

| Mốc | Mục tiêu | Tự kiểm tra |
|---|---|---|
| 0:30 | **CP0** Chuẩn bị | `pytest` chạy được (đỏ hết), đã đọc `data/README.md`, mở xem ≥ 10 ảnh bằng `viz_labels.py` |
| 1:00 | **CP1** Phân loại lỗi | `notes/01_error_taxonomy.md` xong: mỗi mã lỗi ghi máy hay người bắt |
| 3:00 | **CP2** Check cú pháp | `test_missing_labels`, `test_label_format`, `test_class_names`, `test_images`, `test_duplicates`, `test_stats` xanh |
| 4:45 | **CP3** Check ngữ nghĩa + sửa + cửa chặn | `test_second_opinion`, `test_autofix`, `test_gate` xanh; `pytest` xanh hết |
| 4:55 | Nghỉ | |
| 5:30 | **CP4** Calibration | chạy sweep 4 tham số; đã chọn và ghi lý do; `configs/pipeline.yaml` đã đổi |
| 6:00 | **CP5** Pipeline một lệnh | `make run` ra đủ `submission/reports/`; đọc báo cáo, ghi quyết định |
| 6:10 | Bắt đầu train Colab (chạy nền) | `submission/export/clean_v1/` đã commit/push |
| 7:00 | **CP6** Báo cáo + nộp | `make check` hết LỖI; `ANALYSIS.md`, `REPORT.md` xong |

## Chi tiết

**CP1 · cần hiểu.** Vì sao "thiếu file nhãn" máy bắt chắc nhất còn "xe tải gán thành bus" cần người? Lỗi nào *chỉ nghi ngờ* (cảnh báo) chứ không *chắc chắn* (bắt buộc)?

**CP2 · cần hiểu.** `Image.open()` không báo lỗi với ảnh cắt cụt — vì sao phải `load()`? Vì sao md5 không bắt được ảnh thu nhỏ 90%? Đuôi `.JPG` bị bỏ qua thì chuyện gì xảy ra?

**CP3 · cần hiểu.** Vì sao `second_opinion` chỉ **cảnh báo**? Vì sao `autofix` chỉ sửa lỗi cú pháp, không sửa nhãn ngữ nghĩa? Vì sao gate không được bỏ qua lỗi bắt buộc ngay cả ở ảnh đã duyệt?

**CP4 · cần hiểu.** Ngưỡng nào đánh đổi precision lấy recall? Calib chỉ có 39 ảnh — kết luận từ đó có thể sai ở dữ liệu thật ở đâu? (Gợi ý: so số ảnh bị loại ở bước 1 với số ảnh trùng bạn tin là thật.)

**CP5 · cần hiểu.** Hold ≠ Rework. Mã thoát 0/10/20 dùng để làm gì trong CI?

**CP6 · cần hiểu.** Chênh lệch mAP giữa `raw` và `clean` có lớn hơn độ lệch giữa các seed không? Tập test có chứa ảnh trùng với train của `raw` không?
