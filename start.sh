#!/usr/bin/env bash
gunicorn -k gevent --worker-connections 1000 --log-level=info --bind 0.0.0.0:5000 wsgi:app
