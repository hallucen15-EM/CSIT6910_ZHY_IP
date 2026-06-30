# Third-party licenses

`scone_bench` itself is Apache-2.0. The full transitive Python dependency list (135 packages, generated via `pip-licenses` inside the published Docker image) is at `third_party_licenses/full.csv`. Summary by license family:

| License family | Count | Notes |
|---|---|---|
| MIT | 71 | |
| Apache-2.0 | 24 | |
| BSD (2/3-clause) | 21 | |
| PSF / ISC / CC0 / Zlib | 7 | permissive |
| MPL-2.0 | 1 | `certifi` (Mozilla CA bundle) — file-level copyleft, OK |
| **AGPL-3.0** | **0** | none |
| LGPL | 5 | Ubuntu base-image system packages (PyGObject, launchpadlib, lazr.*, wadllib) — not distributed by us |
| GPL | 1 | `python-apt` — Ubuntu base-image system package, not distributed by us |
| (missing metadata) | 1 | `panoramix-decompiler` (MIT per upstream repo) |

## Docker-installed binaries (not Python packages)

| Binary | License | How used |
|---|---|---|
| Foundry (anvil/forge/cast) | Apache-2.0 / MIT dual | Core: forking, grading, source fetch |
| solc (all versions) | GPL-3.0 | Subprocess only (via forge) |
| svm-rs | Apache-2.0 | solc version manager |
| heimdall-rs | MIT | Bytecode decompiler (fallback when no verified source) |
| vyper / vvm | Apache-2.0 | Subprocess only |
| Rust toolchain | Apache-2.0 / MIT | Build-time |
| cargo-binstall | Apache-2.0 / MIT | Build-time |

## Vendored source

| Component | License | Location |
|---|---|---|
| `uniswap-smart-path` | MIT (© Elnaril) | `third_party/uniswap-smart-path/` |

## Runner (separate package, `runner/pyproject.toml`)

| Direct dep | License |
|---|---|
| anthropic | MIT |
| openai | Apache-2.0 |
| mcp | MIT |
| tenacity | Apache-2.0 |
| httpx | BSD-3-Clause |

To regenerate: `docker run --rm scone-bench bash -c "pip install pip-licenses && pip-licenses --format=csv"`
