#!/usr/bin/env python3
"""CLI eval runner for token-audit.

Drives the model via an OpenAI-compatible API against a local MCP server
(written to a temp directory), and writes a transcript JSON per attempt.
"""

import argparse
import asyncio
import csv
import json
import os
import random
import re
from datetime import datetime, timezone
from pathlib import Path

from client import MCPClient
from utils import stream_agentic_response

VULN_CATEGORIES = [
    "overflow", "access_control", "dangerous_call", "logic_error", "replay_race",
]


async def _execute_problem(
    problem_id: str,
    model: str,
    max_tokens: int,
    transcript_path: str,
    timeout: int,
    thinking_budget: int,
):
    """Launch a fresh MCP server for one problem attempt and return the SSE stream."""
    mcp_client = MCPClient(problem_id, model=model)

    return stream_agentic_response(
        mcp_client=mcp_client,
        model=model,
        max_tokens=max_tokens,
        problem_id=problem_id,
        transcript_path=transcript_path,
        thinking_budget=thinking_budget,
    )


async def run_evaluation(
    max_tokens: int,
    problems_metadata_path: str,
    parallel_requests: int,
    transcript_dir: str,
    results_csv: str,
    model: str = "glm-4-plus",
    timeout: int = 10,
    thinking_budget: int = 10000,
) -> None:
    """Run the evaluation with bounded parallelism."""
    with open(problems_metadata_path) as f:
        metadata = json.load(f)["problem_set"]

    problems = metadata.get("problems", [])
    if not problems:
        print("No problems found in metadata file")
        return

    total_runs = len(problems)
    transcript_path_obj = Path(transcript_dir)
    transcript_path_obj.mkdir(parents=True, exist_ok=True)

    pending_tasks: set[asyncio.Task] = set()
    num_completed = 0
    results = []

    async def run_one(problem):
        problem_id = problem["id"]
        if not re.fullmatch(r"[A-Za-z0-9][\w.\-]*", problem_id):
            if not re.fullmatch(r"0x[a-fA-F0-9]{40}", problem_id):
                raise ValueError(f"refusing problem_id {problem_id!r}: invalid characters")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        transcript_path = str(transcript_path_obj / f"{problem_id}_{timestamp}.json")

        print(
            f"problem_id={problem_id} model={model} max_tokens={max_tokens} "
            f"transcript_path={transcript_path} num_running={len(pending_tasks)} "
            f"num_runs={num_completed} total_runs={total_runs}"
        )

        async def execute_with_stream():
            grade_info = None
            token_usage = None
            try:
                async for event in await _execute_problem(
                    problem_id=problem_id,
                    model=model,
                    max_tokens=max_tokens,
                    transcript_path=transcript_path,
                    timeout=timeout,
                    thinking_budget=thinking_budget,
                ):
                    if event.startswith("data: "):
                        try:
                            event_data = json.loads(event[6:])
                            if event_data.get("type") == "grade":
                                grade_info = event_data.get("grade", {})
                            if event_data.get("type") == "token_usage":
                                token_usage = event_data
                        except json.JSONDecodeError:
                            pass
            except RuntimeError as e:
                if "cancel scope" not in str(e).lower():
                    raise

            score = 0.0
            if grade_info:
                score = grade_info.get("score", 0.0)
                if score == 0.0:
                    subscores = grade_info.get("subscores", {})
                    weights = grade_info.get("weights", {})
                    if subscores and weights:
                        score = sum(subscores[k] * weights[k] for k in subscores)

            return {
                "problem_id": problem_id,
                "success": True,
                "transcript_path": transcript_path,
                "score": score,
                "grade_info": grade_info,
                "prompt_tokens": token_usage.get("prompt_tokens", 0) if token_usage else 0,
                "completion_tokens": token_usage.get("completion_tokens", 0) if token_usage else 0,
            }

        try:
            return await asyncio.wait_for(execute_with_stream(), timeout=60 * timeout)
        except TimeoutError:
            print(
                f"Task timed out after {timeout} minutes: problem_id={problem_id} "
                f"transcript_path={transcript_path}"
            )
            return {
                "problem_id": problem_id,
                "success": False,
                "error": "Timeout",
                "score": 0.0,
                "grade_info": None,
                "prompt_tokens": 0,
                "completion_tokens": 0,
            }
        except asyncio.CancelledError:
            print(f"Task was cancelled: problem_id={problem_id}")
            return {
                "problem_id": problem_id,
                "success": False,
                "error": "Task cancelled",
                "score": 0.0,
                "grade_info": None,
                "prompt_tokens": 0,
                "completion_tokens": 0,
            }
        except Exception as e:
            return {
                "problem_id": problem_id,
                "success": False,
                "error": str(e),
                "score": 0.0,
                "grade_info": None,
                "prompt_tokens": 0,
                "completion_tokens": 0,
            }

    for problem in problems:
        if len(pending_tasks) >= parallel_requests:
            done, pending_tasks = await asyncio.wait(pending_tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                results.append(task.result())
                num_completed += 1

        pending_tasks.add(asyncio.create_task(run_one(problem)))
        await asyncio.sleep(random.uniform(1, 3))

    if pending_tasks:
        done = await asyncio.gather(*pending_tasks, return_exceptions=True)
        for result in done:
            if isinstance(result, Exception):
                print(f"Task failed with exception: {result}")
            else:
                results.append(result)
                num_completed += 1

    successful = sum(1 for r in results if r["success"])
    print(f"\nEvaluation complete: {successful}/{total_runs} successful")

    # Summary table
    print("\n--- Results ---")
    for r in results:
        status = "OK" if r["success"] else "FAIL"
        print(f"  {r['problem_id']}: {status} score={r.get('score', 0.0):.2f}")

    errors = [r for r in results if not r["success"]]
    if errors:
        print("\nErrors encountered:")
        for error in errors:
            print(
                f"  {error['problem_id']}: "
                f"{error.get('error', 'Unknown error')}"
            )

    # Write CSV results
    results_csv_path = Path(results_csv)
    results_csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        header = ["contract_address", "prompt_tokens", "completion_tokens", "total_tokens",
                  "score", "ground_truth", "predicted",
                  "precision", "recall", "f1_score"] + VULN_CATEGORIES
        writer.writerow(header)

        scores = []
        precisions = []
        recalls = []
        f1s = []
        prompt_token_sum = 0
        completion_token_sum = 0
        cat_sums = {c: 0.0 for c in VULN_CATEGORIES}
        count = 0

        for r in results:
            addr = r["problem_id"]
            score = r.get("score", 0.0)
            ginfo = r.get("grade_info") or {}

            precision = float(ginfo.get("precision", 0.0) or 0.0)
            recall = float(ginfo.get("recall", 0.0) or 0.0)
            f1 = float(ginfo.get("f1_score", 0.0) or 0.0)

            # parse ground_truth from metadata
            meta = ginfo.get("metadata", {}) or {}
            try:
                gt_dict = json.loads(meta.get("ground_truth", "{}"))
            except (json.JSONDecodeError, TypeError):
                gt_dict = {}
            try:
                predicted_list = json.loads(meta.get("predicted", "[]"))
            except (json.JSONDecodeError, TypeError):
                predicted_list = []

            gt_tags = ":".join(sorted(c for c in VULN_CATEGORIES if gt_dict.get(c)))
            pred_tags = ":".join(sorted(predicted_list))
            subscores = ginfo.get("subscores", {}) or {}
            pt = r.get("prompt_tokens", 0)
            ct = r.get("completion_tokens", 0)
            tt = pt + ct

            row = [addr, pt, ct, tt, f"{score:.4f}", gt_tags, pred_tags,
                   f"{precision:.4f}", f"{recall:.4f}", f"{f1:.4f}"]
            for cat in VULN_CATEGORIES:
                s = subscores.get(cat, 0.0)
                row.append(f"{s:.1f}")
                cat_sums[cat] += s

            writer.writerow(row)
            scores.append(score)
            precisions.append(precision)
            recalls.append(recall)
            f1s.append(f1)
            prompt_token_sum += pt
            completion_token_sum += ct
            count += 1

        if count > 1:
            avg_score = sum(scores) / count
            avg_precision = sum(precisions) / count
            avg_recall = sum(recalls) / count
            avg_f1 = sum(f1s) / count
            avg_pt = prompt_token_sum // count
            avg_ct = completion_token_sum // count
            avg_row = ["average", avg_pt, avg_ct, avg_pt + avg_ct,
                       f"{avg_score:.4f}", "", "",
                       f"{avg_precision:.4f}", f"{avg_recall:.4f}", f"{avg_f1:.4f}"]
            for cat in VULN_CATEGORIES:
                avg_row.append(f"{cat_sums[cat] / count:.4f}")
            writer.writerow([])
            writer.writerow(avg_row)

    print(f"\nResults CSV: {results_csv_path}")


def main():
    parser = argparse.ArgumentParser(description="Run token-audit evaluation")
    parser.add_argument("--max-tokens", type=int, required=True, help="Max output tokens per model turn")
    parser.add_argument("--problems-metadata", type=str, required=True, help="Path to problems metadata JSON")
    parser.add_argument("--parallel-requests", type=int, default=1, help="Max parallel evaluations")
    parser.add_argument("--transcript-dir", type=str, required=True, help="Where to write transcripts")
    parser.add_argument("--results-csv", type=str, default="results/results.csv", help="Path to output CSV")
    parser.add_argument("--model", type=str, default="glm-4-plus", help="Model to use (e.g. glm-4-plus)")
    parser.add_argument("--timeout", type=int, default=30, help="Per-problem timeout in minutes")
    parser.add_argument("--thinking-budget", type=int, default=10000, help="Thinking budget tokens")

    args = parser.parse_args()

    asyncio.run(
        run_evaluation(
            max_tokens=args.max_tokens,
            problems_metadata_path=args.problems_metadata,
            parallel_requests=args.parallel_requests,
            transcript_dir=args.transcript_dir,
            results_csv=args.results_csv,
            model=args.model,
            timeout=args.timeout,
            thinking_budget=args.thinking_budget,
        )
    )


if __name__ == "__main__":
    main()
