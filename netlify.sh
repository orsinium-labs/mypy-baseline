#!/bin/bash
# This script is used by netlify to build docs
set -e
python3 -m pip install '.[docs]'
sphinx-build docs docs/build
