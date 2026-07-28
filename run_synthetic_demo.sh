#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON="$PROJECT_DIR/.venv/bin/python"

if [ ! -x "$PYTHON" ]; then
  echo "The local Python environment was not found."
  echo "Follow the setup instructions in README.md first."
  exit 1
fi

cd "$PROJECT_DIR"
mkdir -p data/uploads

echo "Preparing Jessica's synthetic complete-workflow demonstration..."
"$PYTHON" manage.py migrate --noinput
"$PYTHON" manage.py seed_synthetic_demo

echo ""
echo "Synthetic demo ready at http://127.0.0.1:8000"
echo "Open: Synthetic complete workflow demo"
echo "Expected control result: READY FOR REVIEW"
echo "All figures are made up and not for operational use."
echo "Press Ctrl+C here when the demonstration is finished."
echo ""

exec "$PYTHON" manage.py runserver 127.0.0.1:8000
