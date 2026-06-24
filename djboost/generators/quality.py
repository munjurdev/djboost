def generate_gitignore():
    content = """# ── Python / Django / Venv ────────────────────────────────────────────────────
__pycache__/
*.py[cod]
*$py.class
*.so
env/
venv/
ENV/
.venv/
pyvenv.cfg
*.log
*.pot
*.pyc
*.pyo
*.pyd

# ── Database ──────────────────────────────────────────────────────────────────
db.sqlite3
db.sqlite3-journal
*.sqlite3
*.db
*.dump
*.backup

# ── Static / Media ────────────────────────────────────────────────────────────
/static/
/staticfiles/
/media/
/mediafiles/
/assets/

# ── Secrets ───────────────────────────────────────────────────────────────────
.env
.env.*
*.key
*.pem
*.crt
credentials.json
secrets.json

# ── Celery ────────────────────────────────────────────────────────────────────
celerybeat-schedule*
*.pid

# ── Testing ───────────────────────────────────────────────────────────────────
.coverage
htmlcov/
.pytest_cache/
.tox/
.nox/

# ── IDEs ──────────────────────────────────────────────────────────────────────
.vscode/
.idea/
*.swp
*~

# ── OS ────────────────────────────────────────────────────────────────────────
.DS_Store
Thumbs.db

# ── Docker ────────────────────────────────────────────────────────────────────
docker-compose.override.yml
"""
    with open(".gitignore", "w", encoding="utf-8") as f:
        f.write(content)


def generate_pytest_ini(name: str):
    content = f"""[pytest]
DJANGO_SETTINGS_MODULE = {name}.settings
python_files = tests.py test_*.py *_tests.py
addopts = --cov=. --cov-report=html
"""
    with open("pytest.ini", "w", encoding="utf-8") as f:
        f.write(content)


def generate_pre_commit_config():
    content = """repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black
-   repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
    -   id: isort
-   repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
    -   id: flake8
"""
    with open(".pre-commit-config.yaml", "w", encoding="utf-8") as f:
        f.write(content)
