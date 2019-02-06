.PHONY: clean install clean_release build_release publish_release_testpypi publish_release

clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	rm -Rf *.egg-info
	rm -Rf dist/
	rm -Rf build/

install:
	pip install -e .[dev]

lint:
	flake8

test:
	pytest

build_release: clean
	python setup.py sdist bdist_wheel

publish_release_testpypi: build_release
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

publish_release: build_release
	twine upload dist/*
