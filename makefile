.PHONY: clean init run

# MacOS
ifeq ($(shell uname), Darwin)
    PYTHON   := python3
    PIP      := pip3
# Windows
else ifeq ($(shell uname -p), unknown)
    PYTHON   := python
    PIP      := pip
# Linux Distros
else
    PYTHON   := python3
    PIP      := pip3
endif

clean:
	rm -rf ./assets/calibration_files

init: requirements.txt
	mkdir ./assets/calibration_files
	@if [ -f ./assets/shape_predictor.dat ]; then \
		echo "File exists. Skipping download."; \
	else \
		curl -o ./assets/shape_predictor.dat https://raw.githubusercontent.com/GuoQuanhao/68_points/master/shape_predictor_68_face_landmarks.dat; \
	fi
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) agent_controller.py