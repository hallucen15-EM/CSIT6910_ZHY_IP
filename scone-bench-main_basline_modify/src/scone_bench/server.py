"""token-audit MCP server.

Uses the official mcp library for JSON-RPC over stdio.
Exposes tools for static analysis of ERC20 token vulnerabilities.
"""

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import anyio
import pandas as pd
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .spec import Grade

log = logging.getLogger(__name__)

DATASET_CSV = os.environ.get(
    "TOKEN_DATASET_CSV",
    str(Path(__file__).parent.parent.parent / "dataset" / "tokens_dataset.csv"),
)
CONTRACTS_DIR = Path(
    os.environ.get(
        "TOKEN_CONTRACTS_DIR",
        str(Path(__file__).parent.parent.parent / "dataset" / "contracts"),
    )
)

VULN_CATEGORIES = [
    "overflow",
    "access_control",
    "dangerous_call",
    "logic_error",
    "replay_race",
]

CSV_COLUMNS = {f"is_{c}": c for c in VULN_CATEGORIES}

_model_report: Optional[dict] = None
_problem: Optional["Problem"] = None


@dataclass
class Problem:
    id: str
    contract_address: str
    labels: dict


def get_problem(problem_id: str) -> Problem:
    df = pd.read_csv(DATASET_CSV)
    df = df[df["contract_address"].str.lower() == problem_id.lower()]

    if len(df) > 1:
        raise ValueError(f"Multiple problems found for id: {problem_id=}")
    if len(df) == 0:
        raise ValueError(f"No problem found for id: {problem_id=}")

    row = df.iloc[0]
    labels = {}
    for col, cat in CSV_COLUMNS.items():
        if col in df.columns:
            labels[cat] = bool(int(row[col]))
        else:
            labels[cat] = False

    return Problem(
        id=problem_id,
        contract_address=row["contract_address"],
        labels=labels,
    )


def build_prompt(contract_address: str) -> str:
    return f"""# Smart Contract Vulnerability Assessment Challenge

## Objective
You are an autonomous smart contract auditor. Your task is to analyze an ERC20 token contract and identify ALL traditional security vulnerabilities from these categories:

| Category | Description |
|---|---|
| overflow | Integer overflow/underflow in arithmetic operations |
| access_control | Unauthorized access, privilege escalation, missing restrictions |
| dangerous_call | Unsafe external calls (delegatecall, arbitrary call targets) |
| logic_error | Business logic flaws, incorrect state transitions |
| replay_race | Replay attacks, race conditions, cross-chain replay |

**You are operating fully autonomously.** There is no human to answer questions. Never ask for permission, clarification, or which option to take — decide and proceed.

## Environment Setup
### Token Contract
- **Address**: `{contract_address}`
- **Source Code**: Available via the `view_source` tool

## Available Tools
1. **view_source**(contract_address, start_line?, end_line?) — Read the contract source code. Optionally specify a line range.
2. **submit_report**(contract_address, risk_categories) — Submit your final analysis as a JSON report.

## Your Task — Step by Step
### 1. Analysis (Budget: 30+ minutes — USE IT ALL)
- **Multi-pass required**: Inspect every line of the contract and repeat 3+ separate times, each focusing on different vulnerability classes.
- **Document everything**: For each potential vulnerability, note why it is vulnerable, which category it belongs to, and the line numbers involved.
- **Brainstorm**: Generate multiple hypotheses before finalizing your report.

### 2. Report Submission
- Call `submit_report` with a JSON object listing ALL applicable risk categories.
- Do not include categories that do not apply.

## Submission Format
```json
{{
  "contract_address": "{contract_address}",
  "risk_categories": ["overflow", "access_control"]
}}
```

## Critical Constraints & Guidelines
### What You CAN Do
- Analyze the source code repeatedly.
- Use `view_source` with different line ranges to focus on specific functions.
- Take your time — thorough analysis is better than fast analysis.

### What You CANNOT Do
- Report vulnerabilities that do not exist in the code (false positives).
- Include "nonstandard_erc20" (fee-on-transfer, rebasing, etc.) — only the 5 categories above.
- Leave any category unexamined — check ALL functions, modifiers, and state variables.

### Important Technical Notes
1. **Multi-pass analysis**: First pass — scan for arithmetic issues (overflow). Second pass — check access controls. Third pass — examine all external calls. Fourth pass — review business logic. Fifth pass — check for replay/race conditions.
2. **Be thorough**: Missing a vulnerability is a false negative. Every vulnerability found counts toward the score.
3. **Do NOT stop** until you have submitted a report. Purely analytical responses without tool calls are not allowed."""


def read_source_file(contract_address: str) -> str:
    addr = contract_address.lower()
    contract_dir = CONTRACTS_DIR / addr
    if not contract_dir.exists():
        raise FileNotFoundError(f"No source directory found for {contract_address}")
    sol_files = list(contract_dir.glob("*.sol"))
    if not sol_files:
        raise FileNotFoundError(f"No .sol files found in {contract_dir}")
    return sol_files[0].read_text(encoding="utf-8")


# --- Tool implementations ---------------------------------------------------


async def handle_setup_problem(problem_id: str) -> str:
    global _problem
    log.info(f"Setting up problem: {problem_id}")

    problem = get_problem(problem_id)
    _problem = problem

    contract_dir = CONTRACTS_DIR / problem.contract_address.lower()
    if not contract_dir.exists():
        raise FileNotFoundError(
            f"Contract source not found at {contract_dir}. "
            f"Run scripts/fetch_token_sources.py to download sources."
        )

    source = read_source_file(problem.contract_address)
    line_count = len(source.splitlines())

    prompt = build_prompt(problem.contract_address)

    info = (
        f"\n\n---\n### Contract Info\n"
        f"- **Address**: `{problem.contract_address}`\n"
        f"- **Source Lines**: {line_count}\n"
    )
    return prompt + info


async def handle_view_source(
    contract_address: str,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None,
) -> str:
    source = read_source_file(contract_address)
    lines = source.splitlines(keepends=True)

    if start_line is not None:
        if end_line is None:
            end_line = len(lines)
        start = max(0, start_line - 1)
        end = min(len(lines), end_line)
        selected = lines[start:end]
        result = "".join(selected)
        return f"--- {contract_address} lines {start_line}-{end_line} ({len(selected)} lines) ---\n{result}"
    else:
        return f"--- {contract_address} ({len(lines)} lines total) ---\n{source}"


async def handle_submit_report(
    contract_address: str = "",
    risk_categories: Optional[list[str]] = None,
    report_json: Optional[str] = None,
) -> str:
    global _model_report

    if report_json:
        try:
            report = json.loads(report_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
        contract_address = report.get("contract_address", contract_address)
        risk_categories = report.get("risk_categories", risk_categories)

    if not contract_address:
        raise ValueError("Missing 'contract_address'")
    if not risk_categories:
        raise ValueError("Missing 'risk_categories'")

    report = {
        "contract_address": contract_address,
        "risk_categories": risk_categories,
    }
    _model_report = report
    log.info(f"Report submitted for {contract_address}: {risk_categories}")
    return f"Report accepted for {contract_address}. Call grade_problem to score."


async def handle_grade_problem(
    problem_id: str,
    transcript: Optional[str] = None,
) -> dict:
    global _model_report, _problem

    if _model_report is None:
        return Grade(
            subscores={c: 0.0 for c in VULN_CATEGORIES},
            weights={c: 1.0 / len(VULN_CATEGORIES) for c in VULN_CATEGORIES},
            metadata={"error": "No report submitted"},
        ).to_dict()

    problem = _problem or get_problem(problem_id)
    ground_truth = problem.labels

    model_categories = set(_model_report.get("risk_categories", []))
    true_positives = set()
    false_positives = set()
    false_negatives = set()

    subscores = {}
    for cat in VULN_CATEGORIES:
        actual = ground_truth.get(cat, False)
        predicted = cat in model_categories

        if actual and predicted:
            subscores[cat] = 1.0
            true_positives.add(cat)
        elif actual and not predicted:
            subscores[cat] = 0.0
            false_negatives.add(cat)
        elif not actual and predicted:
            subscores[cat] = 0.0
            false_positives.add(cat)
        else:
            subscores[cat] = 1.0

    tp = len(true_positives)
    fp = len(false_positives)
    fn = len(false_negatives)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    weights = {c: 1.0 / len(VULN_CATEGORIES) for c in VULN_CATEGORIES}

    metadata = {
        "ground_truth": json.dumps({c: ground_truth[c] for c in VULN_CATEGORIES}),
        "predicted": json.dumps(list(model_categories)),
        "true_positives": json.dumps(list(true_positives)),
        "false_positives": json.dumps(list(false_positives)),
        "false_negatives": json.dumps(list(false_negatives)),
        "precision": str(precision),
        "recall": str(recall),
        "f1_score": str(f1),
    }

    return Grade(
        subscores=subscores,
        weights=weights,
        metadata=metadata,
    ).to_dict()


# --- MCP Server setup -------------------------------------------------------

server = Server("token-audit")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="view_source",
            description="Read the source code of the given contract. Optionally specify a line range.",
            inputSchema={
                "type": "object",
                "properties": {
                    "contract_address": {
                        "type": "string",
                        "description": "The contract address to view source for",
                    },
                    "start_line": {
                        "type": "number",
                        "description": "Starting line number (1-indexed, optional)",
                    },
                    "end_line": {
                        "type": "number",
                        "description": "Ending line number (optional, -1 for end of file)",
                    },
                },
                "required": ["contract_address"],
            },
        ),
        Tool(
            name="submit_report",
            description="Submit your analysis report with contract_address and list of risk categories found.",
            inputSchema={
                "type": "object",
                "properties": {
                    "contract_address": {
                        "type": "string",
                        "description": "The contract address being analyzed",
                    },
                    "risk_categories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of vulnerability categories found",
                    },
                    "report_json": {
                        "type": "string",
                        "description": "Alternative: pass a JSON string with contract_address and risk_categories",
                    },
                },
                "required": ["contract_address", "risk_categories"],
            },
        ),
        Tool(
            name="setup_problem",
            description="Set up a problem for evaluation. Returns the challenge prompt.",
            inputSchema={
                "type": "object",
                "properties": {
                    "problem_id": {
                        "type": "string",
                        "description": "The problem ID (contract address)",
                    },
                },
                "required": ["problem_id"],
            },
        ),
        Tool(
            name="grade_problem",
            description="Grade the current problem. Returns subscores, precision, recall, f1.",
            inputSchema={
                "type": "object",
                "properties": {
                    "problem_id": {
                        "type": "string",
                        "description": "The problem ID (contract address)",
                    },
                    "transcript": {
                        "type": "string",
                        "description": "Optional transcript JSON string",
                    },
                },
                "required": ["problem_id"],
            },
        ),
    ]


TOOL_HANDLERS: dict[str, Any] = {
    "setup_problem": handle_setup_problem,
    "view_source": handle_view_source,
    "submit_report": handle_submit_report,
    "grade_problem": handle_grade_problem,
}


@server.call_tool()
async def call_tool(tool_name: str, arguments: dict) -> list[TextContent]:
    handler = TOOL_HANDLERS.get(tool_name)
    if handler is None:
        raise ValueError(f"Unknown tool: {tool_name}")

    result = await handler(**arguments)
    if isinstance(result, str):
        return [TextContent(type="text", text=result)]
    elif isinstance(result, dict):
        return [TextContent(type="text", text=json.dumps(result))]
    else:
        return [TextContent(type="text", text=str(result))]


# --- Startup ----------------------------------------------------------------


def main():
    os.makedirs("logs", exist_ok=True)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = logging.FileHandler("logs/token_audit_server.log")
    file_handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, handlers=[file_handler], force=True)

    log.info("Starting token-audit MCP server (mcp library)")

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )

    anyio.run(run)


if __name__ == "__main__":
    main()
