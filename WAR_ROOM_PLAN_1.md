# WAR_ROOM_PLAN_1.md — Issue #1: Fan-out wiring fix

## Problem
`Circuit.wire()` uses a dict keyed by source node. Second `wire()` call with same source silently overwrites the first, breaking fan-out.

## Checklist
- [x] Fix `wire()` to store multiple destinations per source (use `defaultdict(list)`)
- [x] Fix `evaluate()` to iterate over all wire destinations for each source
- [x] Fix the readiness check in `evaluate()` to look up wires correctly
- [x] Propagate gate outputs along wires so gate-to-gate chains evaluate correctly
- [x] Write regression test (`test_fan_out.py`) that wires one source to two sinks
- [x] Verify Half Adder truth table (4 rows correct)
- [x] Verify Full Adder truth table (8 rows correct)
- [ ] Commit all changes and push
