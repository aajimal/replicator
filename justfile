# Show available commands
default:
    @just --list

# Install package in development mode
install:
    pip install -e .

# Install package and development dependencies
dev-install:
    pip install -e .
    pip install -r requirements-dev.txt

# Run tests with coverage
test:
    pytest tests/ -v --cov=deployment_replicator

# Format code with black
format:
    black deployment_replicator/ tests/

# Run linting and type checking
lint:
    flake8 deployment_replicator/
    mypy deployment_replicator/

# Clean up generated files
clean:
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    rm -rf build/ dist/ *.egg-info
    rm -rf .coverage htmlcov/

# Run example test script
run-example:
    python test_deployment_replicator.py
