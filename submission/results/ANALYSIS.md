# Phân tích: dữ liệu gốc vs dữ liệu sau pipeline

> Số lấy từ `comparison.md` (script sinh). Xoá `TODO(học viên)`.

## 1. Kết quả
Dán bảng từ `comparison.md` và mô tả thiết lập: model, epoch, seed, #ảnh train mỗi biến thể, val, test.

TODO(học viên)

## 2. Chênh lệch có đáng tin không?
TODO(học viên): chênh mAP50 (clean − raw) so với **độ lệch chuẩn giữa các seed**. Với chỉ 2–3 seed bạn kết luận được đến đâu?

## 3. Vì sao có (hoặc không có) khác biệt
TODO(học viên): ≥ 2 giả thuyết, mỗi giả thuyết nêu cách kiểm. Gợi ý để cân nhắc:
- **Yếu tố nhiễu lớn nhất:** 80 ảnh trong `clean` mang nhãn của NGƯỜI (mô phỏng), cùng phong cách với nhãn test. Phần lớn lợi thế của `clean` đến từ đó hay từ việc máy sửa lỗi? Chạy `make run-auto` (không người duyệt) để tách hai phần.
- Test chỉ 100 ảnh: nhiễu lấy mẫu của chính tập test (bootstrap theo ảnh nếu bạn muốn ước lượng), chưa kể val chỉ có vài box `bus`/`truck`. AP theo lớp có đáng tin không?
- `raw` có ảnh **trùng với tập test** (rò rỉ) → điểm raw bị thổi phồng bao nhiêu? Ultralytics tự bỏ ảnh có nhãn hỏng nào, nên "raw" thật sự train trên bao nhiêu ảnh?
- `clean` vẫn còn nhãn pre-label chưa duyệt (hàng đợi > ngân sách): lỗi ngữ nghĩa còn lại là gì?
- Lớp ít ảnh (truck, bus) thay đổi thế nào? Xem AP theo lớp (`ap50_per_class` trong JSON).
- Với 100 ảnh test, một ảnh nhiều box ảnh hưởng mAP bao nhiêu?

## 4. Kết luận trung thực và việc tiếp theo
TODO(học viên)
