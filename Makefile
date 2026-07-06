.PHONY: clean clean-test clean-pyc clean-build docs help lint test test-all coverage dist install check-release bump-major bump-minor bump-patch
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

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts


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

lint: ## check style with ruff
	uv run ruff check datakit tests

test: ## run tests quickly with the default Python
	uv run pytest

test-all: ## run tests on the py310-py313 tox matrix
	uv run tox

coverage: ## check code coverage quickly with the default Python
	uv run coverage run --source datakit -m pytest
	uv run coverage report -m
	uv run coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/datakit.rst
	rm -f docs/modules.rst
	uv run sphinx-apidoc -T -o docs/ datakit
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	uv run watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

check-release: dist ## check release for potential errors
	uv publish --dry-run dist/*

test-release: clean dist ## release distros to test.pypi.org
	uv publish --publish-url https://test.pypi.org/legacy/ dist/*

release: clean dist ## package and upload a release
	uv publish dist/*

dist: clean ## builds source and wheel package
	uv build
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	uv pip install .

bump-major: ## bump the major version, refresh uv.lock, commit, and tag
	@$(MAKE) _bump PART=major

bump-minor: ## bump the minor version, refresh uv.lock, commit, and tag
	@$(MAKE) _bump PART=minor

bump-patch: ## bump the patch version, refresh uv.lock, commit, and tag
	@$(MAKE) _bump PART=patch

_bump:
	@old=$$(grep -m1 '^current_version' setup.cfg | cut -d'=' -f2 | tr -d ' ') && \
	uv run bumpversion $(PART) --no-commit --no-tag --allow-dirty && \
	new=$$(grep -m1 '^current_version' setup.cfg | cut -d'=' -f2 | tr -d ' ') && \
	uv lock && \
	git add setup.cfg pyproject.toml datakit/__init__.py uv.lock && \
	git commit -m "Bump version: $$old → $$new" && \
	git tag "v$$new"
