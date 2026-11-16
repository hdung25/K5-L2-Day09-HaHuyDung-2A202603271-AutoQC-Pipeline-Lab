# Nộp bài

## Repo
Một người **một repo public**. Tên repo: `K5-L23-DAY09-<MSHV>-AutoQCPipeline` (không dấu, nối bằng `-`). Theo hướng dẫn lớp nếu giảng viên đặt quy ước khác.

## Trước khi nộp
1. Đổi dòng tiêu đề `# Day 09 Lab ...` của `README.md`: `# Day 09 Lab — <Họ và tên>: <MSHV> - <Họ và tên>`.
2. Điền `submission/REPORT.md`, `notes/*.md`, `calibration/CALIBRATION.md`, `results/ANALYSIS.md` (xoá mọi dòng `TODO(học viên)`).
3. `make check` (hoặc `python scripts/check_submission.py`) hết **LỖI**.
4. Nộp link repo lên LMS **https://aithucchien.vinuni.edu.vn** hoặc kênh giảng viên chỉ định.

## Cấu trúc bắt buộc
```text
README.md                         # dòng tiêu đề có MSHV - Họ và tên
configs/pipeline.yaml             # ĐÃ calibrate (khác giá trị khởi đầu)
pipeline/ …                       # code của bạn; pytest xanh
submission/
├── REPORT.md                     # tóm tắt + quyết định Release/Hold/Rework + phân việc sửa
├── notes/01_error_taxonomy.md    # phân loại lỗi: máy bắt hay người bắt
├── notes/02_ai_prompts.md        # prompt đã dùng + cách kiểm (nếu không dùng AI: ghi rõ "không dùng")
├── calibration/                  # calibration_report.md|json (script) + CALIBRATION.md (bạn)
├── reports/                      # 01_intake … 08_summary.json, class_stats.csv  (sinh bởi `make run`)
├── export/clean_v1/              # labels/, data.yaml, manifest.json
└── results/                      # raw_seed*.json, clean_seed*.json, comparison.md|json|png, ANALYSIS.md
```
Không commit `work/`, `*.pt`.
