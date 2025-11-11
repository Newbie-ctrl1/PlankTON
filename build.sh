#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Create upload folder
mkdir -p app/static/uploads

# Initialize database if it doesn't exist
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
