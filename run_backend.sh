#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
export PYTHONPATH="${PWD}${PYTHONPATH:+:${PYTHONPATH}}"
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
