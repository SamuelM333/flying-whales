#!/usr/bin/env bash
gunicorn --worker-class eventlet -w 1 --log-level=info --bind 0.0.0.0:5000 wsgi:app
