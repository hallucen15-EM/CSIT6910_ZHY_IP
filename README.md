# TokenAudit — Static-Analysis LLM Benchmark for ERC20 Vulnerabilities

A benchmark that evaluates LLM agents on **classifying ERC20 token contract vulnerabilities** through structured static analysis. Modified from origional scone-bench structure, the agent uses a single `analyze_contract` MCP tool to extract all contract structure, function features, and automated security checks in one call, then submits a `submit_report` with flagged risk categories, without sending full contract source code to LLM.

## Key Features

- **2-round protocol**: `analyze_contract` → `submit_report` — no multi-turn iteration needed
- **Single all-in-one analysis tool**: returns contract info, all functions & state variables, and all 5 vulnerability checks in one response
- **Regex-based Solidity parser**: zero external dependencies, pure Python
- **5 vulnerability categories**: `overflow`, `access_control`, `dangerous_call`, `logic_error`, `replay_race`
- **~70% fewer tokens** vs baseline view_source approach in 50 samples test (avg 5,356 vs 23,191 total tokens/contract)
