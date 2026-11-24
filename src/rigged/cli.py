# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Command-line interface: smoke, run, report, test.

``run`` refuses a confirmatory matrix while its protocol is unfrozen (exit code 2). Exploratory runs
of a registered matrix are allowed only with ``--exploratory`` and only on seeds disjoint from the
confirmatory seeds; they are written under ``results/exploratory/``.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

from .environment import REPO_ROOT
from .matrices import CONFIRMATORY_SEEDS, EXP004_CONTRASTS, EXPLORATORY, REGISTERED, matrix_config
from .protocol_guard import protocol_status
from .report import build
from .runner import run_matrix

EXIT_REFUSED = 2


def _progress(i: int, total: int, rec: dict) -> None:
    if i == total or i % 50 == 0:
        print(f"  {i}/{total} runs ({rec['run_id']}: {rec['status']})", file=sys.stderr)


def cmd_smoke(args) -> int:
    matrix = EXPLORATORY[args.matrix]()
    out = Path(args.out) if args.out else REPO_ROOT / "results" / "exploratory" / matrix.matrix_id.lower()
    print(f"EXPLORATORY matrix {matrix.matrix_id}: {len(matrix.runs())} runs, n = {matrix.n} -> {out}")
    bundle, manifest = run_matrix(matrix, out, None, _command(), progress=_progress)
    print(f"ok {bundle['counts']['ok']}, failed {bundle['counts']['failed']}, wall clock "
          f"{manifest['wall_clock_s']:.2f} s")
    if not args.no_report:
        res = build(out, contrasts=matrix.contrasts, pdf=args.pdf, analytic=matrix.matrix_id != "DEGEN")
        print(json.dumps({k: v for k, v in res.items() if k != "projection"}, indent=1))
        if res.get("projection"):
            print(f"projected full-matrix runtime: {res['projection']['projected_total_s']:.1f} s")
    return 0


def cmd_run(args) -> int:
    if args.experiment not in REGISTERED:
        print(f"unknown experiment {args.experiment}; registered: {sorted(REGISTERED)}", file=sys.stderr)
        return 1
    status = protocol_status(args.experiment, expected_config=matrix_config(REGISTERED[args.experiment]()))
    if not args.exploratory:
        if not status.frozen:
            print(f"REFUSED: {args.experiment} is confirmatory and its protocol is not frozen ({status.reason}). "
                  "Freezing is the owner's decision. Use --exploratory with --seed-offset for an exploratory run.",
                  file=sys.stderr)
            return EXIT_REFUSED
        matrix = REGISTERED[args.experiment]()
        out = Path(args.out) if args.out else REPO_ROOT / "results" / args.experiment
    else:
        seeds = tuple(range(args.seed_offset, args.seed_offset + args.seeds))
        if set(seeds) & set(CONFIRMATORY_SEEDS):
            print("REFUSED: exploratory runs must not use the confirmatory seeds 0 to 19; set --seed-offset >= 20.",
                  file=sys.stderr)
            return EXIT_REFUSED
        kw = {"n": args.n} if args.n else {}
        base = REGISTERED[args.experiment](seeds=seeds, **kw)
        matrix = replace(base, matrix_id=f"{args.experiment}-X", label="exploratory",
                         description=f"EXPLORATORY run of the {args.experiment} draft matrix (seeds {seeds[0]}+)")
        out = Path(args.out) if args.out else REPO_ROOT / "results" / "exploratory" / matrix.matrix_id.lower()
    print(f"{matrix.label.upper()} {matrix.matrix_id}: {len(matrix.runs())} runs -> {out}")
    bundle, manifest = run_matrix(matrix, out, status, _command(), progress=_progress)
    print(f"ok {bundle['counts']['ok']}, failed {bundle['counts']['failed']}, wall clock "
          f"{manifest['wall_clock_s']:.2f} s")
    return 0


def cmd_report(args) -> int:
    if args.input:
        d = Path(args.input)
    elif args.experiment:
        d = REPO_ROOT / "results" / args.experiment
    else:
        print("give --input DIR or --experiment EXP-NNN", file=sys.stderr)
        return 1
    if not (d / "results.json").exists():
        print(f"no results.json in {d}; nothing to report (no run has produced results there)", file=sys.stderr)
        return 1
    matrix_id = json.loads((d / "results.json").read_text(encoding="utf-8")).get("matrix_id", "")
    contrasts = EXP004_CONTRASTS if matrix_id.startswith("EXP-004") else (("d0.50-r1.00", "d0.00-r1.00"),)
    res = build(d, contrasts=contrasts, pdf=args.pdf, analytic=matrix_id != "DEGEN" and not matrix_id.startswith("EXP-004"))
    print(json.dumps({k: v for k, v in res.items() if k != "projection"}, indent=1))
    return 0


def config_path(experiment_id: str) -> Path:
    return REPO_ROOT / "research" / "experiments" / experiment_id / "config.json"


def cmd_export_configs(args) -> int:
    """Write research/experiments/EXP-NNN/config.json from the code (before a freeze only)."""
    for exp_id, build_matrix in sorted(REGISTERED.items()):
        path = config_path(exp_id)
        text = json.dumps(matrix_config(build_matrix()), indent=1, sort_keys=True) + "\n"
        if args.check:
            same = path.exists() and path.read_text(encoding="utf-8") == text
            print(f"{exp_id}: {'matches' if same else 'DIFFERS'} {path.relative_to(REPO_ROOT)}")
            if not same:
                return 1
            continue
        if protocol_status(exp_id).frozen:
            print(f"REFUSED: {exp_id} is frozen; its config is not rewritten", file=sys.stderr)
            return EXIT_REFUSED
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(REPO_ROOT)}")
    return 0


def cmd_test(args) -> int:
    return subprocess.call([sys.executable, "-m", "pytest", "-q", *args.pytest_args], cwd=REPO_ROOT)


def _command() -> str:
    return "python -m rigged.cli " + " ".join(shlex.quote(a) for a in sys.argv[1:])


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="rigged", description="RIGGED simulation study (synthetic data; EXP-004 uses UCI Adult).")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("smoke", help="run an exploratory matrix (SMOKE, SIZING or DEGEN) and its report")
    s.add_argument("--matrix", choices=sorted(EXPLORATORY), default="SMOKE")
    s.add_argument("--out")
    s.add_argument("--pdf", action="store_true")
    s.add_argument("--no-report", action="store_true")
    s.set_defaults(func=cmd_smoke)
    r = sub.add_parser("run", help="run a registered experiment (confirmatory only once frozen)")
    r.add_argument("--experiment", required=True)
    r.add_argument("--exploratory", action="store_true")
    r.add_argument("--seed-offset", type=int, default=1000)
    r.add_argument("--seeds", type=int, default=20)
    r.add_argument("--n", type=int)
    r.add_argument("--out")
    r.set_defaults(func=cmd_run)
    q = sub.add_parser("report", help="build tables, figures and a report from a result directory")
    q.add_argument("--input")
    q.add_argument("--experiment")
    q.add_argument("--pdf", action="store_true")
    q.set_defaults(func=cmd_report)
    e = sub.add_parser("export-configs", help="write (or --check) the confirmatory config files")
    e.add_argument("--check", action="store_true")
    e.set_defaults(func=cmd_export_configs)
    t = sub.add_parser("test", help="run the test suite")
    t.add_argument("pytest_args", nargs="*")
    t.set_defaults(func=cmd_test)
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
