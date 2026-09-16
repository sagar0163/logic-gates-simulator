#!/usr/bin/env python3
"""
Benchmark for Issue #3: replace O(G^2*W) greedy evaluation with a memoized
topological order.

Compares the pre-#3 greedy fixed-point algorithm (O(G^2*W) per evaluation)
with the new memoized topological-order evaluation (O(G+W)) across complete
truth tables (2^n rows) with n = 8..14 inputs.

Usage:
    python3 bench_topo.py            # run the full n = 8..14 sweep
    python3 bench_topo.py 8 10 12    # run a custom set of input counts

The greedy reference is a byte-for-byte copy of the pre-#3 algorithm, so the
two columns measure exactly what the issue describes.
"""

import sys
import timeit
from statistics import median

from gates import Circuit, CircuitError


def old_evaluate_greedy(circuit):
    """Byte-for-byte copy of the pre-#3 greedy fixed-point algorithm."""
    for gate in circuit.gates.values():
        gate.output = False
        for i in range(len(gate.inputs)):
            gate.inputs[i] = False

    for name, value in circuit.inputs.items():
        for gate, idx in circuit.wires[name]:
            circuit.gates[gate].set_input(idx, value)

    evaluated = set()
    while len(evaluated) < len(circuit.gates):
        progress = False
        for name, gate in circuit.gates.items():
            if name in evaluated:
                continue
            ready = True
            for src, dests in circuit.wires.items():
                for g, idx in dests:
                    if g == name:
                        if src in circuit.gates and src not in evaluated:
                            ready = False
                            break
                if not ready:
                    break

            if ready:
                gate.evaluate()
                evaluated.add(name)
                progress = True
                for g, idx in circuit.wires[name]:
                    if g in circuit.gates:
                        circuit.gates[g].set_input(idx, gate.output)

        if not progress:
            cycle_gates = [g for g in circuit.gates if g not in evaluated]
            raise CircuitError(
                f"Cycle detected involving gates: {', '.join(cycle_gates)}")

    result = {}
    for name, source in circuit.outputs.items():
        if source in circuit.gates:
            result[name] = circuit.gates[source].output
    return result


def make_xor_chain(n):
    """n-input XOR reduction chain -> n-1 XOR gates, depth ~n.

    This is a worst-case structure for the greedy fixed-point loop, which
    needs one full pass over all gates per level of depth.
    """
    c = Circuit(f"XOR chain ({n} inputs)")
    for i in range(n):
        c.add_input(f"I{i}", False)
    prev = "I0"
    for i in range(1, n):
        g = f"X{i}"
        c.add_gate(g, "XOR")
        c.wire(prev, g, 0)
        c.wire(f"I{i}", g, 1)
        prev = g
    c.add_output("Z", prev)
    return c


def run_truth_table(circuit, evaluate_fn, n):
    for i in range(2 ** n):
        for j in range(n):
            circuit.set_input(f"I{j}", bool((i >> j) & 1))
        evaluate_fn(circuit)


def bench_truth_table(n, fn, repeats=3):
    """Median wall time over `repeats` full 2^n-row truth tables."""
    times = []
    for _ in range(repeats):
        c = make_xor_chain(n)
        times.append(timeit.timeit(
            lambda: run_truth_table(c, fn, n), number=1))
    return median(times)


def verify_identical(n):
    """Guarantee topo and greedy give byte-identical outputs on all rows."""
    topo_c = make_xor_chain(n)
    greedy_c = make_xor_chain(n)
    for i in range(2 ** n):
        for j in range(n):
            topo_c.set_input(f"I{j}", bool((i >> j) & 1))
            greedy_c.set_input(f"I{j}", bool((i >> j) & 1))
        assert topo_c.evaluate() == old_evaluate_greedy(greedy_c), \
            f"output mismatch at row {i}"


def main(sizes):
    print("Issue #3 benchmark: greedy O(G^2*W) vs memoized topo O(G+W)")
    print("Circuit: n-input XOR-reduction chain (n-1 XOR gates, depth n)")
    print("Timing: median of 3 full 2^n-row truth tables\n")
    print(f"{'n input':>8} | {'rows':>7} | {'gates':>5} | "
          f"{'greedy (s)':>11} | {'topo (s)':>9} | {'speedup':>7}")
    print("-" * 62)
    for n in sizes:
        verify_identical(n)
        reps = 5 if n <= 12 else 3
        greedy_s = bench_truth_table(n, old_evaluate_greedy, reps)
        topo_s = bench_truth_table(n, lambda c: c.evaluate(), reps)
        speedup = greedy_s / topo_s if topo_s else float('inf')
        print(f"{n:>8} | {2**n:>7} | {n-1:>5} | {greedy_s:>11.4f} | "
              f"{topo_s:>9.4f} | {speedup:>6.1f}x")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sizes = [int(a) for a in sys.argv[1:]]
    else:
        sizes = list(range(8, 15))
    main(sizes)