.PHONY: setup test simulate benchmark-sim benchmark-qpu
setup:
	python -m pip install -e ".[dev,quantum]"
test:
	python -m pytest
simulate:
	python -m qprover simulate --n 20
benchmark-sim:
	python -m qprover benchmark --dry-run
benchmark-qpu:
	python -m qprover run --confirm-hardware

