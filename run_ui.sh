#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
export PYTHONPATH="${PWD}${PYTHONPATH:+:${PYTHONPATH}}"
echo "Starting COA Engine backend..."
echo ""
echo "  Dashboard:  http://localhost:8002/dashboard"
echo "  API docs:   http://localhost:8002/docs"
echo "  Health:     http://localhost:8002/health"
echo ""
echo "Press Ctrl+C to stop."
echo ""
exec uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
