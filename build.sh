#!/bin/sh
set -eu

cd "$(dirname "$0")"

echo "Building nvfan standalone binary..."

python -m nuitka \
    --standalone \
    --onefile \
    --include-package=nvitop \
    --output-filename=nvfan \
    gpu-fan-curve.py

echo ""
echo "Build complete: $(ls -lh nvfan | awk '{print $5}') nvfan"
file nvfan
