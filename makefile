.PHONY: init gaze

clean:
	rm -rf assets

init: requirements.txt
	mkdir assets
	curl -o ./assets/shape_predictor.dat https://raw.githubusercontent.com/GuoQuanhao/68_points/master/shape_predictor_68_face_landmarks.dat
	pip install --upgrade pip
	pip install -r requirements.txt

gaze:
	python3 gaze_calibration.py

run: gaze
