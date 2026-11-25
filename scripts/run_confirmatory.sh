#!/bin/sh
# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
# Run one frozen confirmatory experiment through the run guard, then its report and provenance record.
# Usage: scripts/run_confirmatory.sh EXP-NNN    (log: results/EXP-NNN/run.log)
set -u
root="$(cd "$(dirname "$0")/.." && pwd)"
exp="$1"
cd "$root" || exit 1
mkdir -p "results/$exp"
start="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cmd="PYTHONPATH=src nice -n 10 .venv/bin/python -m rigged.cli run --experiment $exp"
PYTHONPATH=src nice -n 10 .venv/bin/python -m rigged.cli run --experiment "$exp" > "results/$exp/run.log" 2>&1
status=$?
end="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "exit status $status" >> "results/$exp/run.log"
if [ "$status" -eq 0 ]; then
  PYTHONPATH=src .venv/bin/python -m rigged.cli report --experiment "$exp" >> "results/$exp/run.log" 2>&1
fi
python3 scripts/write_provenance.py "$exp" "$status" "$start" "$end" "$cmd"
exit "$status"
