# RotorEdge — one-command, KEYLESS reproduction.
PY ?= python

.PHONY: setup data repro verify spec test demo

setup:            ## install pinned deps
	$(PY) -m pip install -r requirements.txt

data:             ## (re)build the frozen keyless snapshot (only needed to refresh data)
	$(PY) scripts/fetch_data.py

repro:            ## run the full walk-forward backtest -> results/ (no API key)
	$(PY) scripts/run_backtest.py

verify:           ## re-run and assert results match the committed reference (no API key)
	$(PY) scripts/verify.py

spec:             ## emit the StrategySpec (add --live for the CMC Agent Hub overlay)
	$(PY) scripts/make_spec.py

test:             ## run the rigor unit tests
	$(PY) -m pytest -q tests || $(PY) tests/run_all.py

demo: repro       ## reproduce, then point to the dashboard
	@echo "Open dashboard/index.html in a browser (data.js was regenerated)."
