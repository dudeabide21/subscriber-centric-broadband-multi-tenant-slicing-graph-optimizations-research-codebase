.PHONY: check-env test parse-samples lint format

PYTHON ?= python
SRC_DIR := src
SAMPLES_DIR := data/samples
PROCESSED_DIR := data/processed

check-env:
	bash scripts/setup/check_environment.sh

test:
	PYTHONPATH=$(SRC_DIR) $(PYTHON) -m pytest

# this line actuate if pip is not installed, but it is not needed if all dependencies are installed in the native environmnet 
 #parse-samples:
	# PYTHONPATH=$(SRC_DIR) $(PYTHON) -m scb.telemetry.sample_processing --samples-dir $(SAMPLES_DIR) --output-dir $(PROCESSED_DIR) 

parse-samples:
	scb-parse-samples --samples-dir $(SAMPLES_DIR) --output-dir $(PROCESSED_DIR)

lint:
	PYTHONPATH=$(SRC_DIR) $(PYTHON) -m ruff check src tests

format:
	PYTHONPATH=$(SRC_DIR) $(PYTHON) -m black src tests