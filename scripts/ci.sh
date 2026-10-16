#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

echo "Running Unit Tests..."
python3 -m pytest tests/ -v

echo "Running Eval Gate..."
python3 evals/harness.py

echo "CI Pipeline Passed! Ready for Deployment."