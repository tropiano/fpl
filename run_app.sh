#!bin/bash
source venv/bin/activate
export DATABASE_URL=postgresql://localhost/fpl
export FLASK_APP=app/__init__.py
flask run