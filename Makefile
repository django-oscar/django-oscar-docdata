.PHONY: clean install clean_release build_release publish_release_testpypi publish_release

clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	find . -name '*.egg-info' -delete

install:
	pip install -e .[dev]

lint:
	flake8

test:
	pytest

clean_release: clean
	if [ -d "dist" ]; then rm dist/*; fi

build_release: clean_release
	python setup.py sdist bdist_wheel

publish_release_testpypi: build_release
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

publish_release: build_release
	twine upload dist/*
