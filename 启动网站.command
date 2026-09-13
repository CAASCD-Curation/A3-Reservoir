#!/bin/zsh
cd "${0:A:h}"
if [[ -x '/Users/chenjuewang1/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3' ]]; then
  exec '/Users/chenjuewang1/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3' scripts/serve.py
else
  exec python3 scripts/serve.py
fi
