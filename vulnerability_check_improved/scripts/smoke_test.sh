#!/usr/bin/env bash
# Copyright 2026 Anthropic PBC
# SPDX-License-Identifier: Apache-2.0
# End-to-end smoke test: build the image, start the MCP server, call
# setup_problem on the smoke task, and verify a problem statement comes back.
set -euo pipefail

cd "$(dirname "$0")/.."

if [ -z "${SCONE_RPC_MAINNET:-}" ] || [ -z "${ETHERSCAN_API_KEY:-}" ]; then
  echo "ERROR: SCONE_RPC_MAINNET and ETHERSCAN_API_KEY must be set (see .env.example)" >&2
  exit 1
fi

echo "[smoke] building image..."
docker build --platform linux/amd64 -t scone-bench . >/dev/null

echo "[smoke] running setup_problem(uerii) inside container..."
docker run --rm -i \
  -e SCONE_RPC_MAINNET \
  -e ETHERSCAN_API_KEY \
  -e COINGECKO_API_KEY \
  -e COVALENT_API_KEY \
  scone-bench \
  python -c '
import asyncio
from scone_bench.server import setup_problem, get_problem
p = get_problem("uerii")
print(f"problem: chain={p.chain} block={p.fork_block_number} target={p.target_contract_address}")
ps = asyncio.run(setup_problem("uerii"))
assert "Smart Contract Vulnerability Assessment Challenge" in ps, "missing header"
assert "127.0.0.1:8545" in ps, "missing RPC endpoint"
print(f"[smoke] OK — problem statement generated ({len(ps)} chars)")
'
