#!/usr/bin/env python3
"""Pre-fetch Solidity source code for tokens from bad_tokens_labeled.csv via Etherscan v2 API.

Usage:
    python scripts/fetch_token_sources.py --limit 5
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests

for line in Path(__file__).parent.parent.joinpath(".env").read_text().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1)
        os.environ.setdefault(k, v)
        
ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY", "")
BASE_URL = "https://api.etherscan.io/v2/api"

CHAINS = [
    ("mainnet", 1),
    ("bsc", 56),
    ("poly", 137),
    ("arbi", 42161),
    ("optim", 10),
    ("base", 8453),
    ("avax", 43114),
    ("sepolia", 11155111),
]

REPO_ROOT = Path(__file__).parent.parent
CONTRACTS_DIR = REPO_ROOT / "dataset" / "contracts"
DATASET_DIR = REPO_ROOT / "dataset"
METADATA_DIR = REPO_ROOT / "problem_metadatas"
DEFAULT_CSV = REPO_ROOT.parent / "bad_tokens_labeled.csv"

VULN_CATEGORIES = [
    "overflow", "access_control", "dangerous_call", "logic_error", "replay_race",
]
CSV_COLUMNS = [f"is_{c}" for c in VULN_CATEGORIES]


def fetch_source(address: str, chainid: int):
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": ETHERSCAN_API_KEY,
        "chainid": chainid,
    }
    resp = requests.get(BASE_URL, params=params, timeout=30)
    data = resp.json()
    if data.get("status") != "1":
        return None
    result = data["result"][0]
    if not result.get("SourceCode"):
        return None
    return result


def save_contract(address: str, info: dict, chain_name: str, chain_id: int) -> None:
    target_dir = CONTRACTS_DIR / address.lower()
    target_dir.mkdir(parents=True, exist_ok=True)

    source_code = info.get("SourceCode", "")
    if not source_code:
        print(f"  WARNING: no source code for {address}", file=sys.stderr)
        return

    if source_code.startswith("{{"):
        source_code = source_code[1:-1]
        try:
            files = json.loads(source_code)
            for path, content in files.get("sources", files).items():
                if isinstance(content, dict):
                    content = content.get("content", "")
                file_path = target_dir / Path(path).name
                file_path.write_text(content, encoding="utf-8")
        except json.JSONDecodeError:
            (target_dir / "contract.sol").write_text(source_code, encoding="utf-8")
    else:
        (target_dir / "contract.sol").write_text(source_code, encoding="utf-8")

    meta = {
        "address": address,
        "chain_name": chain_name,
        "chain_id": chain_id,
        "contract_name": info.get("ContractName", ""),
        "compiler_version": info.get("CompilerVersion", ""),
        "optimization_used": info.get("OptimizationUsed", ""),
        "runs": info.get("Runs", ""),
    }
    (target_dir / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"  OK: {info.get('ContractName', 'unknown')} ({chain_name}) -> {target_dir}")


def generate_metadata_files(rows: list[dict], csv_path: str, metadata_path: str):
    df_out = pd.DataFrame(rows)
    df_out.to_csv(csv_path, index=False)
    print(f"  Wrote {csv_path} ({len(rows)} rows)")

    problems = [{"id": r["contract_address"]} for r in rows]
    metadata = {
        "problem_set": {
            "owner": "token-audit",
            "name": f"token-audit-{len(rows)}",
            "description": f"{len(rows)} token contracts with traditional vulnerability labels",
            "problems": problems,
        }
    }
    Path(metadata_path).parent.mkdir(parents=True, exist_ok=True)
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Wrote {metadata_path} ({len(problems)} problems)")


def main():
    parser = argparse.ArgumentParser(description="Fetch token source code from Etherscan")
    parser.add_argument("--csv", default=str(DEFAULT_CSV), help="Path to bad_tokens_labeled.csv")
    parser.add_argument("--limit", type=int, default=0, help="Number of tokens to fetch (0 = all)")
    parser.add_argument("--skip-nonstandard", action="store_true", default=True,
                        help="Skip nonstandard ERC20 tokens (default: True)")
    args = parser.parse_args()

    if not ETHERSCAN_API_KEY:
        print("ERROR: ETHERSCAN_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"ERROR: CSV not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(csv_path)
    if args.skip_nonstandard and "is_nonstandard_erc20" in df.columns:
        df = df[df["is_nonstandard_erc20"] == 0]
        print(f"Filtered out nonstandard ERC20 tokens, {len(df)} remaining")

    if args.limit > 0:
        df = df.head(args.limit)

    print(f"Processing {len(df)} tokens from {csv_path.name}")

    CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    fetched_rows = []
    for i, (_, row) in enumerate(df.iterrows(), 1):
        addr = row["contract_address"]
        target_dir = CONTRACTS_DIR / addr.lower()
        if target_dir.exists() and (target_dir / "metadata.json").exists():
            print(f"[{i}/{len(df)}] {addr} — already cached, skipping")
            fetched_rows.append(dict(row))
            continue

        print(f"[{i}/{len(df)}] {addr} — trying chains...")
        found = False
        for chain_name, chain_id in CHAINS:
            print(f"  trying {chain_name} (chainid={chain_id})...", end=" ")
            info = fetch_source(addr, chain_id)
            if info:
                print("found")
                save_contract(addr, info, chain_name, chain_id)
                found = True
                break
            else:
                print("no source")
            time.sleep(0.2)

        if found:
            fetched_rows.append(dict(row))
        else:
            print(f"  FAILED: no source found for {addr}", file=sys.stderr)
        time.sleep(0.3)

    if fetched_rows:
        n = len(fetched_rows)
        dataset_csv = DATASET_DIR / "tokens_dataset.csv"
        metadata_json = METADATA_DIR / f"token-audit-{n}.json"
        generate_metadata_files(fetched_rows, str(dataset_csv), str(metadata_json))
        print(f"\nDone. {n}/{len(df)} tokens fetched successfully.")
        print(f"Run eval with: --problems-metadata {metadata_json}")
    else:
        print("\nNo tokens fetched.")


if __name__ == "__main__":
    main()
