#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONUNBUFFERED=1
export HOST_YARN_PORT="${HOST_YARN_PORT:-8099}"
export HOST_YARN_BIND="${HOST_YARN_BIND:-0.0.0.0}"
exec python3 -m host_yarn_bridge.app
