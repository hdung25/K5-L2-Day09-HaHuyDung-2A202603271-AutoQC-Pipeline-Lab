# Checkpoints — Day 09

Bài cá nhân, dự kiến **4–4,5 giờ**; Colab chạy nền ~20 phút. Mốc tính từ lúc bắt đầu, là điểm **tự kiểm tra**, không phải hạn nộp.

| Mốc | Mục tiêu | Tự kiểm tra |
|---|---|---|
| 0:20 | **CP1** Chuẩn bị | `pytest` chạy được (46 failed, 18 passed), đã đọc `data/README.md` và 4 check viết sẵn |
| 2:20 | **CP2** 5 module | `test_label_format`, `test_duplicates`, `test_second_opinion`, `test_autofix`, `test_gate` xanh; `pytest` xanh hết |
| 3:00 | **CP3** Calibrate + CVAT nhẹ | `make calibrate` chạy; đã chọn 2 ngưỡng và ghi lý do; `configs/pipeline.yaml` đã đổi |
| 3:30 | **CP4** Chạy và train | `make run` ra đủ `reports/`; đã push `export/clean_v1/` và bấm Run all trên Colab |
| 4:15 | **CP5** Báo cáo + nộp | `make check` hết LỖI; `REPORT.md` xong |

## Cần hiểu ở mỗi mốc

**CP1.** Vì sao "thiếu file nhãn" máy bắt chắc nhất còn "xe tải gán thành bus" cần người? `Image.open()` không báo lỗi với ảnh cắt cụt: vì sao phải `load()`?

**CP2.** Vì sao md5 không bắt được ảnh thu nhỏ 90%? Vì sao `second_opinion` chỉ **cảnh báo**? Vì sao `autofix` chỉ sửa lỗi cú pháp, không sửa nhãn ngữ nghĩa? Vì sao gate không được bỏ qua lỗi bắt buộc kể cả ở ảnh đã duyệt?

**CP3.** Ngưỡng nào đánh đổi precision lấy recall? Calib chỉ có 39 ảnh: kết luận từ đó có thể sai ở dữ liệu thật ở đâu?

**CP4.** Hold ≠ Rework. Mã thoát 0/10/20 dùng để làm gì trong CI?

**CP5.** Chênh lệch mAP giữa `raw` và `clean` có lớn hơn độ lệch giữa các seed không? Tập test có chứa ảnh trùng với train của `raw` không?
