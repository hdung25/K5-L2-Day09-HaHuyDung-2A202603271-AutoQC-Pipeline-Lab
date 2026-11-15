# Lệnh tắt. Chạy từ thư mục gốc repo. Windows không có make: chạy trực tiếp các lệnh python bên dưới.
PY ?= python
export PYTHONUTF8=1

test:            ## chạy unit test (tiến độ của bạn: xanh hết = xong phần code)
	$(PY) -m pytest -q

calibrate:       ## chạy đủ 5 sweep và ghi submission/calibration/calibration_report.md
	$(PY) -m pipeline.calibrate --sweep duplicates.phash_dist=2,4,6,8,10,12,14,16,20 --sweep label_format.overflow_tol=0,0.001,0.002,0.005,0.01,0.02 --sweep second_opinion.conf=0.25,0.4,0.5,0.6,0.7,0.8 --sweep second_opinion.iou_loose=0.4,0.5,0.6,0.7 --sweep second_opinion.fp_conf=0.1,0.15,0.25,0.4 --out submission/calibration

run:             ## MỘT LỆNH chạy cả pipeline. Mã thoát 0=Release 10=Hold 20=Rework (Hold là kết quả hợp lệ, make không coi là lỗi)
	$(PY) -m pipeline.run; rc=$$?; test $$rc -le 20 || exit $$rc

run-auto:        ## thí nghiệm: không có người duyệt -> submission/export/clean_auto (biến thể `auto` khi train)
	$(PY) -m pipeline.run --budget 0 --export-name clean_auto --reports work/reports_auto

train:           ## train raw vs clean (cần GPU; nên chạy trên Colab)
	$(PY) scripts/train_compare.py --variants raw clean --seeds 0 1 2 --epochs 40
	$(PY) scripts/summarize_results.py

check:           ## kiểm tra bài nộp
	$(PY) scripts/check_submission.py

all: test run check
