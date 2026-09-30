.PHONY: install test lint typecheck check clean run

install:        ## Create the venv and install all dependencies
	python -m venv venv
	venv/Scripts/python -m pip install -U pip
	venv/Scripts/python -m pip install -e ".[dev]"

test:           ## Run the test suite
	venv/Scripts/python -m pytest

lint:           ## Run the linter
	venv/Scripts/python -m ruff check src tests

typecheck:      ## Run static type checks
	venv/Scripts/python -m mypy

check: lint typecheck test  ## Run all quality gates

run:            ## Start the bot locally
	venv/Scripts/python -m pricebot

clean:          ## Remove build and cache artifacts
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache
	find src tests -type d -name __pycache__ -exec rm -rf {} +
