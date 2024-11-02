init:
	python3 -m venv venv
	pip install --upgrade pip
	. ./venv/bin/activate; pip install -r requirements.txt

format:
	. ./venv/bin/activate; black .
