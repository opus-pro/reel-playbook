#!/usr/bin/env bash
# Builds the planted-defect test video (needs ffmpeg) instead of committing a binary.
set -eu
python "$(dirname "$0")/../../../../tests/hooks/make_fixture.py" .
rm -rf segs
