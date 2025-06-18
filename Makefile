.PHONY: install dev-install test format lint clean run-example

install:
	pip install -e .

dev-install:
	pip install -e .
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v --cov=deployment_replicator

format:
	black deployment_replicator/ tests/

lint:
	flake8 deployment_replicator/
	mypy deployment_replicator/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info
	rm -rf .coverage htmlcov/

run-example:
	python test_deployment_replicator.py