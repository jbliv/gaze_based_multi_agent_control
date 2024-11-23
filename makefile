.PHONY: init gaze

init: requirements.txt
	pip install --upgrade pip
	pip install -r requirements.txt

gaze:
	python3 gaze_calibration.py

run: init gaze