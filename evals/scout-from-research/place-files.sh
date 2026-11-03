#!/usr/bin/env bash
# Copies the saved research (scout.py output) into the sandbox, so the case runs offline.
set -eu
cp -r "$(dirname "$0")/files/research" .
