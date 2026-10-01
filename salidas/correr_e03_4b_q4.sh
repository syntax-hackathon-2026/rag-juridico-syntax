#!/usr/bin/env bash
# Corrida e03_4b_q4: igual que e02_v0 pero con el decoder plan B (Qwen3-4B-Instruct-2507 Q4_K_M).
cd "$(dirname "$0")/.."
export SYNTAX_LLM=qwen3-4b-2507-q4
nohup .venv/bin/python -u src/generacion/modelo.py servir > salidas/llama_server_4b.log 2>&1 &
until grep -q "listening" salidas/llama_server_4b.log 2>/dev/null; do sleep 2; done
caffeinate -i .venv/bin/python -u src/main.py --split sample --experimento e03_4b_q4 > salidas/e03_4b_q4.log 2>&1
echo "FIN exit=$?" >> salidas/e03_4b_q4.log
