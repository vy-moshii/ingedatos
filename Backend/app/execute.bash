#!/usr/bin/env bash
set -e
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000