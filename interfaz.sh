#!/usr/bin/env bash
# Interfaz grafica (Streamlit). Requiere el indice y llama-server para "Consultar";
# "Explorar entrega" funciona sin ellos.
exec streamlit run src/interfaz/app.py "$@"
