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
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

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
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
    - if: $CI_MERGE_REQUEST_ID
"""
    with open(".gitlab-ci.yml", "w", encoding="utf-8") as f:
        f.write(content)
