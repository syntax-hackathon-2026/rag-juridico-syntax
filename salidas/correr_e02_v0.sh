#!/usr/bin/env bash
# Corrida e02_v0 desacoplada de la terminal: sobrevive al cierre de Cursor; caffeinate evita que el Mac duerma.
cd "$(dirname "$0")/.."
nohup .venv/bin/python -u src/generacion/modelo.py servir > salidas/llama_server.log 2>&1 &
until grep -q "listening" salidas/llama_server.log 2>/dev/null; do sleep 2; done
caffeinate -i .venv/bin/python -u src/main.py --split sample --experimento e02_v0 > salidas/e02_v0.log 2>&1
echo "FIN exit=$?" >> salidas/e02_v0.log
