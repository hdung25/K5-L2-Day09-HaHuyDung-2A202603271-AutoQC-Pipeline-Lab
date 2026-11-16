# Kiến trúc pipeline

Năm bước như slide Day 09 (máy: 1, 4, 5 · người: 3). Bước 2 (pre-label) **giảng viên đã làm trước khi lô tới tay bạn**: ảnh trong `data/raw` đã có nhãn từ yolo26n, bạn không chạy model gán nhãn. QC tự động là **cửa chặn** trước khi xuất.

| Bước | Vào | Ra | Ai | Code |
|---|---|---|---|---|
| 1 Nhận | ảnh thô `data/raw` | ảnh sạch (loại hỏng / nhỏ / trùng / rò rỉ test) | máy | `steps/intake.py` → `checks/images.py`, `checks/duplicates.py` |
| 2 Pre-label | — | nhãn nháp (yolo26n) | model, **đã làm sẵn** | (ngoài phạm vi bài lab) |
| 3 Gán, sửa | hàng đợi ưu tiên | nhãn đã sửa | **người** (mô phỏng) | `steps/review_queue.py`, `scripts/human_review_sim.py` |
| 4 QC | nhãn | báo cáo lỗi + quyết định | máy | `checks/*.py`, `steps/autofix.py`, `steps/gate.py` |
| 5 Xuất | nhãn đạt | dataset + `manifest.json` | máy | `steps/export.py` |

## Luồng chạy của `python -m pipeline.run`

```
raw ──▶ [1 intake] ──▶ ds/ ──▶ [4 QC vòng 1] ──▶ 02_error_list_v1   (lỗi TRƯỚC khi sửa)
                                    │
                                    ▼
                      [4 autofix]  ──▶ 03_fixes.csv
                                    │
                                    ▼
                          [4 QC vòng 2] ──▶ 04_error_list_v2 ──▶ 05_review_queue.csv
                                    │
                                    ▼
                  [3 người duyệt, ngân sách N ảnh] ──▶ 06_review_log.csv
                                    │
                                    ▼
                  [4 QC vòng 3 + gate] ──▶ 07_error_list_v3 + kết luận
                          │                          │
               còn lỗi bắt buộc               không còn lỗi bắt buộc
                          ▼                          ▼
                  Rework: KHÔNG xuất        Release (phát hành) hoặc Hold (bản NHÁP): [5 export]
```
Thư mục làm việc `work/run/ds/` là **bản sao**: pipeline không bao giờ sửa `data/raw`.

## Các mã lỗi

`severity`: **E** = lỗi bắt buộc (chặn pipeline; máy sửa hoặc loại ảnh) · **W** = cảnh báo (chuyển người xem).

| Mã | Sev | Check | Nghĩa | Ví dụ trong slide |
|---|:-:|---|---|---|
| `CORRUPT_IMAGE` | E | images | ảnh không mở được | "Ảnh hỏng không mở được" |
| `BAD_SIZE` | E | images | cạnh ngắn dưới `min_side_px` | "Kích thước: đúng độ phân giải yêu cầu" |
| `DUP_IMAGE_EXACT` | E | duplicates | trùng từng byte (md5) | "Hai ảnh giống hệt khác tên" |
| `DUP_IMAGE_NEAR` | E | duplicates | trùng gần đúng (perceptual hash) | "Ảnh thu nhỏ 90%" |
| `LEAK_TEST` | E | duplicates | ảnh trùng với tập test/val | "Metric đẹp giả" |
| `MISSING_LABEL_FILE` | E | missing_labels | có ảnh, không có `.txt` (máy không bịa nhãn: `autofix` ghi `needs_label`, người gán) | "Ảnh 042 không có file .txt" |
| `BAD_FORMAT` | E | label_format | dòng không đủ 5 cột số | "Dòng nhãn thiếu cột" |
| `BAD_CLASS_ID` | E | label_format | ID lớp ngoài 0..3 | "ID lớp 93" |
| `BOX_ZERO` | E | label_format | rộng hoặc cao bằng 0 | "Box rộng hoặc cao bằng 0" |
| `BOX_OUT_OF_IMAGE` | E | label_format | box tràn ra ngoài ảnh | "Box tràn ra ngoài ảnh" |
| `DUP_BOX` | E | label_format | hai box cùng lớp gần như trùng | (thêm) |
| `BAD_CLASS_NAME` | E | class_names | tên lớp ngoài danh sách / sai chỗ | "Car, pedestrian" |
| `ORPHAN_LABEL` | W | missing_labels | nhãn không có ảnh | "nhãn không có ảnh" |
| `EMPTY_LABEL` | W | missing_labels | file nhãn rỗng | "Ảnh nền không có vật thể" |
| `BOX_TINY` | W | label_format | box nhỏ hơn `min_box_px` | "Lọc box nhỏ" |
| `BOX_HUGE` | W | label_format | box phủ gần hết ảnh | "box quá lớn" |
| `CLASS_RARE` | W | stats | lớp có quá ít box | "Lớp 93 chỉ có 1 box" |
| `DENSE_IMAGE` | W | stats | ảnh có quá nhiều box | (thêm) |
| `POSSIBLE_MISSING` | W | second_opinion | model thấy vật, nhãn không có box | "Thiếu nhãn" |
| `POSSIBLE_WRONG_CLASS` | W | second_opinion | cùng vị trí, khác lớp | "Xe tải gán thành bus" |
| `POSSIBLE_LOOSE_BOX` | W | second_opinion | đúng vật, IoU thấp | "Box lỏng" |
| `POSSIBLE_FALSE_POS` | W | second_opinion | box nhãn không khớp vật nào | "Thừa" (Day 07) |

Mọi dòng báo cáo có dạng *tên file, số dòng, mã, lý do* — "mỗi dòng là một chỗ cần mở" (slide).

## Mã thoát

`0` Release · `10` Hold · `20` Rework · `1` script lỗi.
**Hold vẫn xuất `export/clean_v1/`** nhưng là **bản nháp** (`manifest.json` ghi `decision: Hold`) để bạn thử nghiệm train; **không** được gọi là bản phát hành. Rework thì không xuất. Dùng trong CI: `python -m pipeline.run || echo "mã $?"`.
