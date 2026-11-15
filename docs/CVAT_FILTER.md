# CVAT: lọc box bất thường (tuỳ chọn, +2 điểm thưởng)

Pipeline tìm lỗi trên **toàn bộ** dữ liệu; CVAT dùng để **xem và sửa tay** vài ca. Slide Day 09, mục "Dùng công cụ kiểm có sẵn".

1. Tạo project CVAT (nhãn `car, person, truck, bus` theo đúng thứ tự), tạo task từ ~20 ảnh trong `work/run/ds/images/`
   (lấy từ đầu `05_review_queue.csv`), import nhãn dạng *YOLO 1.1* (zip gồm `obj.names`, `obj.data`, `train.txt`, `obj_train_data/*.txt`).
2. Mở **Filters** của job → *Add rule*:
   - box nhỏ: `width < 20` (hoặc `height < 20`);
   - theo lớp: `label=="truck"`;
   - ca khó: `attr["can_review"]==true`.
3. Duyệt bằng `→` / `←` (nhảy tới/lui ảnh khớp bộ lọc), `Tab` (chuyển object), `Del` (xoá 1 box).
4. **Trước khi xoá hàng loạt** (`Ctrl+E` → *Remove filtered shapes*): đếm box khớp, `Ctrl+S`, chắc chắn bộ lọc hiển thị đúng tập cần xoá.
5. Export YOLO 1.1, so sánh với nhãn pipeline: CVAT sửa gì mà pipeline chưa thấy?

Nộp: ảnh chụp bộ lọc + 3–5 dòng nhận xét trong `REPORT.md` (mục "CVAT").
