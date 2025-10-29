find . -type d -name "__pycache__" -o -name "*.pyc" -o -name ".venv" -o -name ".pytest_cache" -o -name "*.egg-info" 2>/dev/null | head -20
