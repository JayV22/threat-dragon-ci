#!/usr/bin/env python3
import json
import glob
import argparse
import os
from pathlib import Path

SEVERITY_MAP = {
    "High": 5,
    "Medium": 3,
    "Low": 1,
    "Critical": 8
}

def score_threat(threat):
    # Threat Dragon threat fields may vary; attempt to read 'severity' or 'likelihood'/'impact'
    severity = threat.get("severity") or threat.get("threatType") or threat.get("likelihood")
    # Normalize
    if isinstance(severity, str):
        sev = severity.capitalize()
        base = SEVERITY_MAP.get(sev, 2)
    else:
        try:
            base = int(severity)
        except Exception:
            base = 2
    # Check mitigation
    mitigation = threat.get("mitigation") or threat.get("remediation") or ""
    mitigated = bool(mitigation and mitigation.strip())
    effective = base * (0.5 if mitigated else 1.0)
    return effective

def compute_model_score(model_json):
    total = 0.0
    threats = []
    # Threat Dragon v2 stores threats under model.threats or diagram.components[*].threats
    if "threats" in model_json:
        threats = model_json["threats"]
    else:
        # Explore diagram components
        diagram = model_json.get("diagram") or {}
        components = diagram.get("components") or []
        for c in components:
            for t in c.get("threats", []):
                threats.append(t)
    for t in threats:
        total += score_threat(t)
    return total, len(threats)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description="Analyze Threat Dragon JSON models and compute exposure scores.")
    parser.add_argument("--models", nargs="+", required=True, help="List of model JSON files (supports glob expansion).")
    parser.add_argument("--output", default="exposure.json", help="Where to write exposure results.")
    args = parser.parse_args()
    results = {}
    for pattern in args.models:
        for path in sorted(glob.glob(pattern)):
            try:
                model = load_json(path)
            except Exception as e:
                print(f"Failed to load {path}: {e}")
                continue
            score, count = compute_model_score(model)
            results[path] = {"score": score, "threat_count": count}
            print(f"Model: {path} -> score={score:.2f}, threats={count}")
    with open(args.output, "w") as of:
        json.dump(results, of, indent=2)
    print(f"Wrote exposure summary to {args.output}")

if __name__ == '__main__':
    main()
