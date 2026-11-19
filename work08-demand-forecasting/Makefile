.PHONY: all data train test demo clean

export PYTHONPATH := src

all: data train test demo

data:
	python3 scripts/generate_dataset.py

train:
	python3 scripts/run_pipeline.py

test:
	python3 -m pytest -v tests

demo:
	python3 scripts/demo_offline.py
	python3 scripts/demo_forecast.py

clean:
	rm -rf artifacts/*.joblib __pycache__ .pytest_cache
