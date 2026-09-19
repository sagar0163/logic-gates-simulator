# WAR ROOM PLAN #5 — pip-installable package + LICENSE

## Status: RESUMED from prior attempt (branch war-room-issue-5)

Prior attempts already committed: package dir, pyproject.toml, MIT LICENSE, README
rewrite, console script, `gates.py` shim, tests updated to import `logic_gates`.
The last commit changed the project name to `logic_gates` (from `logic-gates-simulator`)
but that change was never verified by a fresh install.

## Subtasks

- [x] Move logic into `logic_gates/` package with `__init__.py`, `__main__.py` (done in prior commits)
- [x] Add `pyproject.toml` (PEP 621), zero runtime deps, `logic-gates` console script (done)
- [x] Add MIT `LICENSE` and wire it into pyproject (done)
- [x] Keep `gates.py` as a thin backward-compat shim (done)
- [x] Update README with install-based usage (done)
- [x] Update tests to import `logic_gates` (done)
- [x] Set project name to `logic_gates` and VERIFY fresh-venv `pip install .`
- [x] Verify `from logic_gates import ANDGate` works from any directory in fresh venv
- [x] Verify `logic-gates` console command and `python -m logic_gates` run demos
- [x] Verify no third-party runtime dep installed (`pip show` / dependency audit)
- [x] Verify `pip show logic_gates` reports MIT license
- [ ] Run test suite from repo root
- [ ] Clean leftover scratch/generated files out of git (pyc, stray txt)
- [ ] Final commit, delete plan file, push branch