#!/usr/bin/env python3
"""Generate placeholder Solidity source files for tokens from bad_tokens_labeled.csv.

Usage:
    python scripts/generate_placeholder_sources.py --limit 5
"""

import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).parent.parent
CONTRACTS_DIR = REPO_ROOT / "dataset" / "contracts"
DATASET_DIR = REPO_ROOT / "dataset"
METADATA_DIR = REPO_ROOT / "problem_metadatas"
DEFAULT_CSV = REPO_ROOT.parent / "bad_tokens_labeled.csv"

VULN_CATEGORIES = [
    "overflow", "access_control", "dangerous_call", "logic_error", "replay_race",
]
CSV_COLUMNS = [f"is_{c}" for c in VULN_CATEGORIES]

VULN_SNIPPETS = {
    "overflow": r"""    // VULNERABILITY: integer underflow - no sufficient balance check
    function transfer_ovf(address _to, uint256 _value) public returns (bool success) {
        balanceOf[msg.sender] -= _value;
        balanceOf[_to] += _value;
        Transfer(msg.sender, _to, _value);
        return true;
    }

    function transferFrom_ovf(address _from, address _to, uint256 _value) public returns (bool success) {
        allowance[_from][msg.sender] -= _value;
        balanceOf[_from] -= _value;
        balanceOf[_to] += _value;
        Transfer(_from, _to, _value);
        return true;
    }

    function batchTransfer(address[] _recipients, uint256 _value) public {
        uint256 total = _recipients.length * _value;
        require(balanceOf[msg.sender] >= total);
        balanceOf[msg.sender] -= total;
        for (uint256 i = 0; i < _recipients.length; i++) {
            balanceOf[_recipients[i]] += _value;
        }
    }""",

    "access_control": r"""    // VULNERABILITY: setOwner has no access control - anyone can become owner
    function setOwner(address _newOwner) public {
        owner = _newOwner;
    }

    // VULNERABILITY: mint protected by onlyOwner, but setOwner allows anyone to become owner
    function mint(address _to, uint256 _amount) public {
        require(msg.sender == owner);
        totalSupply += _amount;
        balanceOf[_to] += _amount;
        Transfer(address(0), _to, _amount);
    }""",

    "dangerous_call": r"""    // VULNERABILITY: arbitrary delegatecall to user-controlled address
    function delegate(address _target, bytes _data) public payable {
        require(msg.sender == owner);
        _target.delegatecall(_data);
    }

    // VULNERABILITY: arbitrary external call with no gas limits
    function execute(address _target, uint256 _value, bytes _data) public {
        _target.call.value(_value)(_data);
    }

    function setLogicContract(address _logic) public {
        require(msg.sender == owner);
        logicContract = _logic;
    }""",

    "logic_error": r"""    // VULNERABILITY: logic error - assignment instead of comparison (tradingEnabled = true vs ==)
    function transfer_ler(address _to, uint256 _value) public returns (bool success) {
        if (tradingEnabled = true) {
            require(balanceOf[msg.sender] >= _value);
            balanceOf[msg.sender] -= _value;
            balanceOf[_to] += _value;
            Transfer(msg.sender, _to, _value);
            return true;
        }
        return false;
    }

    function transferFrom_ler(address _from, address _to, uint256 _value) public returns (bool success) {
        require(balanceOf[_from] >= _value);
        require(allowance[_from][msg.sender] >= _value);
        allowance[_from][msg.sender] -= _value;
        balanceOf[_from] -= _value;
        balanceOf[_to] += _value;
        Transfer(_from, _to, _value);
        return true;
    }

    // VULNERABILITY: anyone can burn any address's tokens
    function burnFrom(address _from, uint256 _value) public {
        balanceOf[_from] -= _value;
        totalSupply -= _value;
        Transfer(_from, address(0), _value);
    }""",

    "replay_race": r"""    // VULNERABILITY: replay attack - no nonce tracking
    function permitTransfer(
        address _from, address _to, uint256 _value,
        uint8 _v, bytes32 _r, bytes32 _s
    ) public {
        bytes32 hash = keccak256(abi.encodePacked(_from, _to, _value));
        address signer = ecrecover(hash, _v, _r, _s);
        require(signer == _from);

        require(balanceOf[_from] >= _value);
        balanceOf[_from] -= _value;
        balanceOf[_to] += _value;
        Transfer(_from, _to, _value);
    }""",
}

BASE_CONTRACT_TEMPLATE = r"""// SPDX-License-Identifier: MIT
pragma solidity ^0.4.16;

contract {name} {{
    string public name = "{token_name}";
    string public symbol = "{symbol}";
    uint8 public decimals = 18;
    uint256 public totalSupply;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    address public owner;
    bool public tradingEnabled = false;
    address public logicContract;

    function {constructor_name}() public {{
        owner = msg.sender;
        totalSupply = 1000000 * (10 ** 18);
        balanceOf[owner] = totalSupply;
    }}

    {functions}

    function transfer(address _to, uint256 _value) public returns (bool success) {{
        require(balanceOf[msg.sender] >= _value);
        balanceOf[msg.sender] -= _value;
        balanceOf[_to] += _value;
        Transfer(msg.sender, _to, _value);
        return true;
    }}

    event Transfer(address indexed _from, address indexed _to, uint256 _value);
    event Approval(address indexed _owner, address indexed _spender, uint256 _value);
}}
"""


def get_active_categories(row: dict) -> list[str]:
    return [cat for cat in VULN_CATEGORIES if row.get(f"is_{cat}", 0) == 1]


def make_symbol(seed: str) -> str:
    base = "".join(c for c in seed.upper() if c.isalnum())
    return base[:5] if base else "TOKN"


def make_contract(contract_name: str, token_name: str, categories: list[str]) -> str:
    functions = []
    for cat in categories:
        snippet = VULN_SNIPPETS.get(cat, "")
        if snippet:
            functions.append(snippet)
    funcs_str = "\n\n".join(functions)
    return BASE_CONTRACT_TEMPLATE.format(
        name=contract_name,
        token_name=token_name,
        symbol=make_symbol(contract_name),
        constructor_name=contract_name,
        functions=funcs_str,
    )


def generate_metadata_files(rows: list[dict], csv_path: str, metadata_path: str):
    df_out = pd.DataFrame(rows)
    df_out.to_csv(csv_path, index=False)
    print(f"  Wrote {csv_path} ({len(rows)} rows)")

    problems = [{"id": r["contract_address"]} for r in rows]
    metadata = {
        "problem_set": {
            "owner": "token-audit",
            "name": f"token-audit-{len(rows)}",
            "description": f"{len(rows)} token contracts (placeholders)",
            "problems": problems,
        }
    }
    Path(metadata_path).parent.mkdir(parents=True, exist_ok=True)
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Wrote {metadata_path} ({len(problems)} problems)")


def main():
    parser = argparse.ArgumentParser(description="Generate placeholder token contracts from CSV")
    parser.add_argument("--csv", default=str(DEFAULT_CSV), help="Path to bad_tokens_labeled.csv")
    parser.add_argument("--limit", type=int, default=0, help="Number of tokens to process (0 = all)")
    parser.add_argument("--skip-nonstandard", action="store_true", default=True,
                        help="Skip nonstandard ERC20 tokens (default: True)")
    args = parser.parse_args()

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

    print(f"Generating {len(df)} placeholder contracts from {csv_path.name}")

    CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    for i, (_, row) in enumerate(df.iterrows(), 1):
        addr = row["contract_address"]
        categories = get_active_categories(row.to_dict())
        cat_str = "+".join(categories) if categories else "none"
        token_name = row.get("token_name", f"Token_{addr[:8]}")

        contract_name = f"PlaceholderToken_{i}"
        code = make_contract(contract_name, token_name, categories)

        target_dir = CONTRACTS_DIR / addr.lower()
        target_dir.mkdir(parents=True, exist_ok=True)

        (target_dir / "contract.sol").write_text(code)

        meta = {
            "contract_name": contract_name,
            "compiler_version": "v0.4.16+commit.d01c3939",
            "vulnerability": ",".join(categories),
        }
        (target_dir / "metadata.json").write_text(json.dumps(meta, indent=2))
        print(f"  [{i}/{len(df)}] {addr[:12]}... ({cat_str}) -> {target_dir}")

        rows.append(dict(row))

    n = len(rows)
    dataset_csv = DATASET_DIR / "tokens_dataset.csv"
    metadata_json = METADATA_DIR / f"token-audit-{n}.json"
    generate_metadata_files(rows, str(dataset_csv), str(metadata_json))
    print(f"\nDone. {n} placeholder contracts generated.")
    print(f"Run eval with: --problems-metadata {metadata_json}")


if __name__ == "__main__":
    main()
