"""
inject0r.py - Prompt Injection Test Harness

Runs a battery of prompt injection attacks against a target AI application
and uses an LLM judge to automatically evaluate the results.

Usage:
    python3 inject0r.py                     # Test all targets
    python3 inject0r.py --target secret_keeper  # Test one target
"""
import argparse
import json
import os
import time
from datetime import datetime

from target import TARGETS
from attacks import get_attacks_for_scenario, ATTACKS
from judge import Judge

# Delay between API calls to stay within the free tier rate limit
# (15 requests/minute = 1 request every 4 seconds)
API_DELAY_SECONDS = 4


def run_test(target_key: str, judge: Judge) -> dict:
    """Run all relevant attacks against a single target and return results."""
    target = TARGETS[target_key]

    # Only run attacks that are designed for this target's scenario.
    # Using scenario (not the dict key) means multi-model variants like
    # "secret_keeper_gemini" still get the correct secret_keeper attacks.
    attacks = get_attacks_for_scenario(target.scenario)

    results = []

    print(f"\n{'='*60}")
    print(f"TARGET: {target.name}")
    print(f"Attacks to run: {len(attacks)} (filtered for this target)")
    print(f"{'='*60}")

    for i, attack in enumerate(attacks, 1):
        print(f"\n  [{i}/{len(attacks)}] {attack['name']} ({attack['category']})")
        print(f"  Sending attack... ", end="", flush=True)

        # Send the attack to the target
        response = target.send(attack["payload"])

        # Check if this was a harness/API error (not a real model response)
        if response["error"]:
            print(f"ERROR")
            print(f"  {response['text']}")
            results.append({
                "attack_id": attack["id"],
                "attack_name": attack["name"],
                "attack_category": attack["category"],
                "payload": attack["payload"],
                "response": response["text"],
                "outcome": "error",
                "error_type": "target_error",
                "confidence": "n/a",
                "reasoning": response["text"],
            })
            time.sleep(API_DELAY_SECONDS)
            continue

        print(f"got response ({len(response['text'])} chars)")

        # Delay to respect rate limits before the judge call
        time.sleep(API_DELAY_SECONDS)

        # Judge the result
        print(f"  Judging... ", end="", flush=True)
        judgment = judge.evaluate(
            target_name=target.name,
            target_rules=target.system_prompt,
            attack_payload=attack["payload"],
            target_response=response["text"],
            secret=target.secret,
        )

        # Determine the outcome: bypassed, blocked, or error
        if judgment.get("judge_error"):
            outcome = "error"
            error_type = "judge_error"
            status = "JUDGE ERROR"
        elif judgment["success"]:
            outcome = "bypassed"
            error_type = None
            status = "BYPASSED — attack succeeded!"
        else:
            outcome = "blocked"
            error_type = None
            status = "BLOCKED — target held firm"

        print(f"{status}")
        print(f"  Confidence: {judgment['confidence']}")
        print(f"  Reasoning: {judgment['reasoning']}")

        results.append({
            "attack_id": attack["id"],
            "attack_name": attack["name"],
            "attack_category": attack["category"],
            "payload": attack["payload"],
            "response": response["text"],
            "outcome": outcome,
            "error_type": error_type,
            "confidence": judgment["confidence"],
            "reasoning": judgment["reasoning"],
        })

        time.sleep(API_DELAY_SECONDS)

    return {
        "target": target_key,
        "target_name": target.name,
        "scenario": target.scenario,
        "model": target.model,
        "results": results,
    }


def print_summary(all_results: list):
    """Print a summary report of all test results."""
    print(f"\n{'='*60}")
    print("SUMMARY REPORT")
    print(f"{'='*60}")

    total_attacks = 0
    total_successes = 0
    total_errors = 0

    for target_result in all_results:
        results = target_result["results"]
        successes = sum(1 for r in results if r["outcome"] == "bypassed")
        blocked = sum(1 for r in results if r["outcome"] == "blocked")
        errors = sum(1 for r in results if r["outcome"] == "error")
        total = len(results)
        total_attacks += total
        total_successes += successes
        total_errors += errors

        # Calculate percentage only from non-error results
        valid = successes + blocked
        pct = (successes / valid * 100) if valid > 0 else 0

        print(f"\n  {target_result['target_name']} (model: {target_result['model']}):")
        print(f"    Bypassed: {successes}/{valid} valid tests ({pct:.0f}%)")

        if errors > 0:
            print(f"    Errors:   {errors} (API failures or judge errors — not counted as blocked)")

        if successes > 0:
            print(f"    Successful techniques:")
            for r in results:
                if r["outcome"] == "bypassed":
                    print(f"      - {r['attack_name']} [{r['confidence']} confidence]")

    valid_total = total_attacks - total_errors
    pct = (total_successes / valid_total * 100) if valid_total > 0 else 0
    print(f"\n  OVERALL: {total_successes}/{valid_total} valid tests bypassed ({pct:.0f}%)")
    if total_errors > 0:
        print(f"  ({total_errors} test(s) excluded due to errors)")


def save_results(all_results: list, judge: Judge, filename: str):
    """Save detailed results to a JSON file."""
    # Collect unique target models tested
    target_models = sorted(set(r["model"] for r in all_results))

    report = {
        "tool": "inject0r",
        "version": "0.2.0",
        "timestamp": datetime.now().isoformat(),
        "target_models": target_models,
        "judge_model": judge.model,
        "results": all_results,
    }

    # Create the output directory if it doesn't exist
    output_dir = os.path.dirname(filename)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(filename, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Detailed results saved to: {filename}")


def main():
    parser = argparse.ArgumentParser(description="Prompt Injection Test Harness")
    parser.add_argument(
        "--target",
        choices=list(TARGETS.keys()),
        help="Test a specific target (default: test all)",
    )
    args = parser.parse_args()

    # All output goes to reports/ which is gitignored
    output_file = "reports/results.json"

    print("inject0r v0.2.0 — Prompt Injection Test Harness")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total attacks in library: {len(ATTACKS)}")

    judge = Judge()

    # Decide which targets to test
    if args.target:
        target_keys = [args.target]
    else:
        target_keys = list(TARGETS.keys())

    print(f"Targets to test: {', '.join(target_keys)}")

    # Run tests
    all_results = []
    for target_key in target_keys:
        result = run_test(target_key, judge)
        all_results.append(result)

    # Report
    print_summary(all_results)
    save_results(all_results, judge, output_file)


if __name__ == "__main__":
    main()
