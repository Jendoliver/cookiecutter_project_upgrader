.PHONY: clean clean-test clean-pyc clean-build clean-mypy docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test clean-mypy ## remove all caches and build artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

clean-mypy: ## remove mypy cache
	rm -fr .mypy_cache/

build: install-dev test flake8 mypy ## execute automated tooling to build and test the project in the current python version

flake8: ## check style with flake8 (lint)
	flake8 cookiecutter_project_upgrader tests --max-line-length=120

mypy: ## check types with mypy
	mypy cookiecutter_project_upgrader tests/__init__.py  tests/files.py  tests/test_cli.py  tests/test_logic.py  tests/tmp_files.py

test: ## run all tests with the current python env
	pytest

tox: ## run tests and other checks on every Python version with tox
	tox

coverage: ## check code coverage with the current python env
	pytest --cov=cookiecutter_project_upgrader --cov-report=xml:.dev/coverage/coverage.xml
	coverage report -m
	coverage html --directory .dev/coverage/htmlcov
	$(BROWSER) .dev/coverage/htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/cookiecutter_project_upgrader.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ cookiecutter_project_upgrader
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	twine upload dist/*

dist: clean-build ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: ## install the package to the active Python's site-packages (production-mode)
	pip install --upgrade .

install-dev: ## install the package for development
	pip install -e .[dev]

install-dev-upgrade: ## install-dev + upgrade any dependencies if possible
	pip install --upgrade -e .[dev]
