#!/bin/bash
echo "Starting app..."
python -c "import app" 2>&1 || { echo "Failed to import app module"; exit 1; }
exec gunicorn app:app --log-level debug --log-file=- --error-logfile=-
