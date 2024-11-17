.PHONY: init

init: requirements.txt
	pip install --upgrade pip
	pip install -r requirements.txt