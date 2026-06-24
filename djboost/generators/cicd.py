import os


def generate_github_actions():
    """Generate GitHub Actions CI workflow."""
    os.makedirs(".github/workflows", exist_ok=True)
    content = """name: Django CI

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Lint with flake8
      run: flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

    - name: Run tests
      run: pytest
"""
    with open(".github/workflows/main.yml", "w", encoding="utf-8") as f:
        f.write(content)


def generate_gitlab_ci():
    """Generate GitLab CI pipeline."""
    content = """image: python:3.11-slim

stages:
  - test

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip

test:
  stage: test
  before_script:
    - python -m pip install --upgrade pip
    - pip install -r requirements.txt
  script:
    - flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    - pytest
"""
    with open(".gitlab-ci.yml", "w", encoding="utf-8") as f:
        f.write(content)
