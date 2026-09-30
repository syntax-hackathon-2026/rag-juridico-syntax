#!/usr/bin/env bash
# Comando unico de reproduccion: envoltorio fino de src/main.py (toda la logica vive en Python).
#   bash run.sh                 # sample_50 -> salidas/sample_<experimento>.jsonl
#   bash run.sh --split test    # test_992  -> submissions.jsonl
# Requiere el decoder servido en local: python src/generacion/modelo.py servir
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-python}"
[ -x .venv/bin/python ] && PY=.venv/bin/python
if [ "$#" -eq 0 ]; then set -- --split sample; fi
exec "$PY" src/main.py "$@"
