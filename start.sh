#!/usr/bin/env bash
gunicorn --workers 1 --log-level=info --bind 0.0.0.0:8080 wsgi:app
