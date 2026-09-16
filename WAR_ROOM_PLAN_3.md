# WAR ROOM PLAN — Issue #3

[PERF][P1] Replace O(G²·W) greedy evaluation with memoized topological order.

Prior attempt already landed: memoized topo evaluation (`8da24dc`), reference/golden
tests (`0b8b589`), benchmark + recorded numbers (`f9a8d50`), `.gitignore` cleanup
(`fde6407`), and a consolidation commit (`293b741`). This plan resumes from there.

## Checklist

- [x] Memoized topological order (Kahn) built once in `Circuit._build_topo_order`
- [x] `evaluate()` walks topo order in a single O(G+W) pass
- [x] Cache invalidation on `add_gate`
- [x] Cache invalidation on `wire`
- [x] Cycle detection via leftover-nodes in Kahn
- [x] Golden truth-table vectors (Full Adder, fan-out)
- [x] Differential test vs byte-for-byte old greedy algorithm on random acyclic circuits
- [x] `bench_topo.py` (n = 8..14 truth tables) + `bench_topo_results.txt`
- [x] `.gitignore` build artifacts (`__pycache__`, `*.pyc`, `.pytest_cache`)
- [x] Cache invalidation on `add_input` (structural input change) + test
- [x] Confirm `set_input` (value-only change) does NOT invalidate cache + test
- [x] Ignore untracked `build/` and `*.egg-info/` artifacts
- [ ] Run full test suite + benchmark sanity run
- [ ] Remove this plan file and final commit
- [ ] Push branch `war-room-issue-3`
