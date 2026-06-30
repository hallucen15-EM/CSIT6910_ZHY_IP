#!/usr/bin/env python3
# Copyright 2026 Anthropic PBC
# SPDX-License-Identifier: Apache-2.0
"""Regenerate problem_metadatas/scone-bench-local.json from dataset/scone_bench.csv."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
csv_path = ROOT / "dataset" / "scone_bench.csv"
out_path = ROOT / "problem_metadatas" / "scone-bench-local.json"

problems = []
with open(csv_path) as f:
    for row in csv.DictReader(f):
        problems.append(
            {
                "image": "scone-bench",
                "startup_command": "uv --offline --directory /mcp_server run scone_bench mcp",
                "id": row["case_name"],
            }
        )

out = {
    "problem_set": {
        "owner": "scone-bench",
        "name": "scone-bench",
        "description": "417 historical DeFi exploit tasks",
        "problems": problems,
    }
}

out_path.write_text(json.dumps(out, indent=2))
print(f"wrote {len(problems)} problems → {out_path}")
