#!/bin/bash
# This script is used by netlify to build docs
set -e
python3 -m pip install '.[docs]'
cp -r assets docs/
sphinx-build docs docs/build
