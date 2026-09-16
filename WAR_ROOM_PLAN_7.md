# WAR ROOM PLAN — Issue #7: Circuit save/load via strict-validated JSON

## Subtasks

- [ ] Implement `Circuit.to_json()` / `Circuit.from_json()` in `gates.py` (no eval/exec/pickle; strict key/type/wire validation with clear `CircuitError`s)
- [ ] Write `test_serialization.py`: round-trip truth-table tests (each gate + both adder demos)
- [ ] Write malformed-input tests: truncated JSON, unknown gate type, wire to nonexistent gate, cyclic wire, unknown keys — must raise clear errors, never hang
- [ ] Create example circuit file `examples/half_adder.json`
- [ ] Document the JSON format in `README.md`
- [ ] Run full test suite (`python -m pytest` + `python -m unittest`) and fix failures
- [ ] Grep-check regression: no `eval(`, `exec(`, or `pickle` in load path