#!/bin/bash
# This script is used by netlify to build docs
set -e
python3 -m pip install --break-system-packages '.[docs]'
cp -r assets docs/
python3 -m sphinx docs docs/build
