.PHONY: init gaze

clean:
	rm -rf ./assets/calibration_files

init: requirements.txt
	mkdir ./assets/calibration_files
	@if [ -f ./assets/shape_predictor.dat ]; then \
		echo "File exists. Skipping download."; \
	else \
		curl -o ./assets/shape_predictor.dat https://raw.githubusercontent.com/GuoQuanhao/68_points/master/shape_predictor_68_face_landmarks.dat; \
	fi
	pip install --upgrade pip
	pip install -r requirements.txt

gaze:
	python3 gaze_calibration.py

run: gaze
