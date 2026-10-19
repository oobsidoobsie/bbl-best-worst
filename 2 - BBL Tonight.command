#!/bin/bash
# Builds the Best & Worst tables and the Top 10 image for one night of NBA games.
cd "$(dirname "$0")" || exit 1
if [ ! -x .venv/bin/python ]; then
  echo "Run '1 - Setup' first (double-click it)."; read -n 1 -s -r -p "Press any key to close"; exit 1
fi
ARGS=("$@")
if [ ${#ARGS[@]} -eq 0 ]; then
  echo "🏀 BBL Best & Worst"
  echo "Press Enter for the latest night, type a date like 20261020, or type demo for the sample:"
  read -r D
  if [ "$D" = "demo" ]; then ARGS=(--demo); elif [ -n "$D" ]; then ARGS=("$D"); fi
fi
.venv/bin/python bbl/run.py "${ARGS[@]}"
echo
read -n 1 -s -r -p "Press any key to close"
