#!/usr/bin/env bash
# Rebuild the README images. Needs Python 3, Google Chrome and network access for the web fonts.
set -euo pipefail
cd "$(dirname "$0")"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
python3 scorecard.py
python3 proof.py
shot() {
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
    --virtual-time-budget=8000 --window-size="1600,$2" --screenshot="$PWD/../$1.png" "file://$PWD/$1.html" >/dev/null 2>&1
}
shot hero 800
shot pipeline 1100
shot formula 920
shot scorecard 850
shot proof 1040
