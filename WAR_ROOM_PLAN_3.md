# WAR_ROOM_PLAN_3.md — Issue #3: Replace O(G²·W) greedy with memoized topo order

- [ ] 1. Add `_topo_cache` and `_topo_valid` fields to `Circuit.__init__`; invalidate on wire/gate/add_gate changes
- [ ] 2. Implement `_build_topo_order()` using Kahn's algorithm (fan-in adjacency + in-degree)
- [ ] 3. Replace `evaluate()` body with single-pass O(G+W) traversal in topo order
- [ ] 4. Verify cycle detection still works (Kahn's leftover nodes → CircuitError)
- [ ] 5. Write golden correctness test: all acyclic circuits produce byte-identical outputs
- [ ] 6. Write benchmark script `bench_topo.py` (timeit over truth tables n=8..14)
- [ ] 7. Run benchmarks, record before/after numbers
- [ ] 8. Run full test suite; fix any regressions
- [ ] 9. Final commit + delete plan file
