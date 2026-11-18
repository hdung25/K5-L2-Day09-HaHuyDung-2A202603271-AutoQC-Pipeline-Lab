# Hướng dẫn phần Google Colab (train raw vs clean) — bạn tự làm

Phần train là **tùy chọn, chấm riêng 15 điểm**. Mọi thứ khác (4 module, calibrate, pipeline, báo cáo) đã xong và `make check-core` sạch.
Tổng thời gian: ~5 phút thao tác + ~20 phút chờ GPU chạy.

## Bước 0 — Đưa code lên GitHub (nhánh `main`, repo **public**)

Notebook clone repo bằng `git clone --depth 1` nên chỉ thấy nhánh **mặc định (`main`)**. Toàn bộ bài làm đang ở nhánh
`claude/analysis-processing-guidelines-8c37aa`, cần đưa vào `main` rồi push:

```powershell
cd D:\vinuni\lab03\day09\K5-L2-Day09-HaHuyDung-2A202603271-AutoQC-Pipeline-Lab
```
```powershell
git merge claude/analysis-processing-guidelines-8c37aa
```
```powershell
git push origin main
```

Kiểm tra trên trình duyệt: `https://github.com/hdung25/K5-L2-Day09-HaHuyDung-2A202603271-AutoQC-Pipeline-Lab` phải là **Public**
(Settings → General → Danger Zone → Change visibility) và có file `submission/export/clean_v1/manifest.json`.

## Bước 1 — Mở notebook trên Colab

Mở link này (đã điền sẵn repo của bạn):

https://colab.research.google.com/github/hdung25/K5-L2-Day09-HaHuyDung-2A202603271-AutoQC-Pipeline-Lab/blob/main/notebooks/day09_train_compare.ipynb

Hoặc: Colab → File → Open notebook → tab **GitHub** → dán URL repo → chọn `notebooks/day09_train_compare.ipynb`.

## Bước 2 — Bật GPU

Runtime → **Change runtime type** → Hardware accelerator: **T4 GPU** → Save.

## Bước 3 — Sửa ô cấu hình (ô code đầu tiên)

```python
REPO_URL = "https://github.com/hdung25/K5-L2-Day09-HaHuyDung-2A202603271-AutoQC-Pipeline-Lab.git"
SEEDS = [0, 1]
EPOCHS = 20
VARIANTS = ["raw", "clean"]
```
**Không đổi** `SEEDS`, `EPOCHS`, `VARIANTS` (rubric yêu cầu cùng siêu tham số, ≥ 2 seed; `check_submission.py` kiểm điều này).

## Bước 4 — Runtime → **Run all**, rồi kiểm tra từng ô

| Ô | Bạn phải thấy |
|---|---|
| 2 (GPU + clone) | `Tesla T4`, và `git log` có các commit `label_format: ...`, `REPORT: ...` |
| 4 (kiểm export) | `quyết định pipeline: Hold` và `số ảnh train của clean: 202` |
| 6 (train) | 4 lần train (raw/clean × seed 0/1), mỗi lần ~3–5 phút. Ultralytics sẽ in cảnh báo ảnh hỏng/nhãn hỏng của `raw`: **chụp/ghi lại** (dùng cho báo cáo) |
| 7 (tổng hợp) | bảng `comparison.md` + hình `comparison.png` |
| 10 (lưu) | trình duyệt tải về `results.zip` |

Nếu ô 4 báo thiếu `manifest.json` → bạn chưa push `main` (quay lại Bước 0).
Nếu hết quota GPU → dùng Kaggle Notebook (bật GPU + Internet) chạy y hệt.

## Bước 5 — Đưa kết quả về repo

1. Giải nén `results.zip` vào thư mục repo sao cho có `submission/results/raw_seed0.json`, `raw_seed1.json`, `clean_seed0.json`, `clean_seed1.json`, `comparison.md`, `comparison.json`, `comparison.png`. **Không sửa tay** các file này.
2. Chạy kiểm tra đầy đủ:
```powershell
$env:PYTHONUTF8=1; .\.venv\Scripts\python scripts/check_submission.py
```
   (Nếu chưa có `.venv` ở thư mục gốc: `python -m venv .venv; .\.venv\Scripts\python -m pip install -r requirements.txt`.)

## Bước 6 — Điền mục 5 của `submission/REPORT.md`

Thay đoạn "**Chưa chạy** …" bằng (gửi mình file `comparison.md` là mình viết giúp được):
1. Dán bảng từ `submission/results/comparison.md` (model yolo26n, 20 epoch, seed 0/1, số ảnh train: raw 224 / clean 202).
2. Tính **Δ mAP50 = clean − raw** và so với **độ lệch chuẩn giữa 2 seed** của mỗi biến thể. Nếu |Δ| ≤ độ lệch chuẩn → viết "**chưa kết luận được, khác biệt nằm trong nhiễu**", không viết "clean tốt hơn".
3. ≥ 2 nguyên nhân + cách kiểm (đã đặt giả thuyết sẵn trong báo cáo):
   - `raw` chứa **5 ảnh trùng test** (`img_0049, img_0101, img_0167, img_0174, img_0221` ↔ `test_033, 039, 044, 085, 009`) ⇒ có thể thổi phồng mAP của `raw`; kiểm: so AP của 2 model trên 5 ảnh test đó vs 95 ảnh còn lại.
   - `clean` còn 38 ảnh có cảnh báo chưa duyệt (chủ yếu box lỏng, `FALSE_POS`) ⇒ hạn chế mức cải thiện; kiểm: biến thể `oracle` (thêm vào `VARIANTS`) làm chặn trên.
   - Test chỉ 100 ảnh, lớp `truck`/`bus` ít box (41/32 box trong `class_stats.csv`) ⇒ AP theo lớp dao động mạnh (xem ô 8).
4. Kết luận trung thực + việc tiếp theo (thêm seed, duyệt thêm 18 ảnh để Release, chạy `oracle`).

## Bước 7 — Commit và nộp

```powershell
git add submission/results submission/REPORT.md
```
```powershell
git commit -m "Thêm kết quả train Colab raw vs clean (2 seed) và mục 5 báo cáo"
```
```powershell
git push origin main
```
Rồi nộp link repo lên LMS (https://aithucchien.vinuni.edu.vn).
