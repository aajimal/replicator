from setuptools import setup, find_packages

setup(
    name="deployment-replicator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0",
        "GitPython>=3.1",
        "PyYAML>=6.0",
        "Jinja2>=3.0",
        "colorama>=0.4",
        "tabulate>=0.9",
    ],
    entry_points={
        "console_scripts": [
            "deploy-replicate=deployment_replicator.cli:cli",
        ],
    },
    python_requires=">=3.8",
)