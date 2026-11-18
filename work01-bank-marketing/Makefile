PYTHON ?= python3
export PYTHONPATH := src

.PHONY: all data test lock clean

lock:
	$(PYTHON) -m work01 lock

all:
	$(PYTHON) -m work01 all

data:
	$(PYTHON) -m work01 data

test:
	$(PYTHON) -m work01 test

clean:
	rm -rf artifacts data/raw data/processed .pytest_cache