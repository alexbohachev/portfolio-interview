PYTHON ?= python3
export PYTHONPATH := src

.PHONY: all seed test lock

lock:
	$(PYTHON) -m work02 lock

seed:
	$(PYTHON) -m work02 seed

all:
	$(PYTHON) -m work02 all

test:
	$(PYTHON) -m work02 test