#! /bin/sh
CURRENT=$(cd $(dirname $0);pwd)
export TOML_PATH=${CURRENT}/docker/gennet/config.toml
export OUTDIR_PATH=${CURRENT}/generated

uv run src/gennet/main.py
