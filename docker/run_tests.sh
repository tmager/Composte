#!/usr/bin/env bash

set -e

eval "$(pyenv init -)"

pyenv activate composte

pytest tests --cov-report html

echo "Running MyPy..."
mypy .

echo "Running black..."
black --quiet wf_db tests*

echo "Running flake8..."
flake8 .

echo "Running bandit..."
bandit -r .

echo "Running iSort..."
isort --recursive --apply .
