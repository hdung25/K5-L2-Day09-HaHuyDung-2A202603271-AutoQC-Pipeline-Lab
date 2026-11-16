# Train trên Google Colab

[![Mở trong Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Haiduongcable/L23-Day09-AutoQC-Pipeline-Lab/blob/main/notebooks/day09_train_compare.ipynb)
*(badge trỏ vào repo mẫu; với repo của bạn đổi `Haiduongcable/L23-Day09-AutoQC-Pipeline-Lab` thành `<tài-khoản>/<tên-repo>`. Repo phải **public**.)*

Chỉ phần **train** cần GPU (T4 miễn phí). Pipeline, calibration và báo cáo chạy ngay trên máy bạn.

```mermaid
flowchart LR
  L["Máy bạn<br/>pytest · make calibrate · make run"] -->|"git push<br/>submission/export/clean_v1"| G[GitHub public]
  G --> C["Colab T4<br/>train raw / clean (≥ 2 seed)"]
  C -->|"tải results/*.json"| L
  L --> A["summarize_results.py<br/>+ ANALYSIS.md"]
```

1. Chạy `make run` (đã Release/Hold), **commit và push** `submission/export/clean_v1/` (kèm `manifest.json`).
2. Mở notebook từ badge trên (hoặc Colab → File → Open notebook → GitHub → dán URL repo). Runtime → **T4 GPU**.
3. Chạy lần lượt các ô: cài đặt, clone repo của bạn, train `raw` và `clean` với ≥ 2 seed (khuyến nghị 3), tải `results/*.json` về `submission/results/`.
4. Trên máy: `python scripts/summarize_results.py` → `comparison.md`, rồi viết `ANALYSIS.md`.

**Hết quota GPU?** Kaggle Notebook (bật Internet) chạy y hệt; hoặc rút gọn cục bộ `--epochs 15 --imgsz 416 --device cpu` (ghi rõ cấu hình rút gọn trong `ANALYSIS.md`).
Chênh lệch giữa raw và clean thường **nằm trong nhiễu** (test 100 ảnh): hãy báo cáo trung thực.
