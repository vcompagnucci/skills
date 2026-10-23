#!/bin/bash
# Abre el editor de las fotos del proyecto. El servidor local (solo esta Mac, 127.0.0.1) sirve la
# carpeta y arma las exportaciones desde las maestras de 16 bits (recipe/editor_server.py).
cd "$(dirname "$0")"
PORT=8775
while lsof -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; do PORT=$((PORT+1)); done
(sleep 1; open "http://127.0.0.1:$PORT/editor.html") &
exec .venv/bin/python recipe/editor_server.py $PORT
