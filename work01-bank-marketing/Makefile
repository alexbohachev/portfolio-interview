PYTHON ?= python3
export PYTHONPATH := src

.PHONY: all data test clean

all:
	$(PYTHON) -m work01 all

data:
	$(PYTHON) -m work01 data

test:
	$(PYTHON) -m work01 test

clean:
	rm -rf artifacts data/raw data/processed .pytest_cache