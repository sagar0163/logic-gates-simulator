#!/usr/bin/env python3
"""Regression tests for Issue #3: memoized topological-order evaluation.

Ensures the new O(G+W) evaluation is byte-identical to the previous greedy
O(G²·W) algorithm on all acyclic circuits, that the memoized topo order is
invalidated when the circuit changes, and that cycles are still caught.
"""

import random
import unittest

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


def make_full_adder():
    c = Circuit("Full Adder")
    c.add_gate('XOR1', 'XOR')
    c.add_gate('XOR2', 'XOR')
    c.add_gate('AND1', 'AND')
    c.add_gate('AND2', 'AND')
    c.add_gate('OR1', 'OR')
    c.add_input('A', False)
    c.add_input('B', False)
    c.add_input('Cin', False)
    c.add_output('Sum', 'XOR2')
    c.add_output('Carry', 'OR1')
    c.wire('A', 'XOR1', 0)
    c.wire('B', 'XOR1', 1)
    c.wire('Cin', 'XOR2', 1)
    c.wire('XOR1', 'XOR2', 0)
    c.wire('A', 'AND1', 0)
    c.wire('B', 'AND1', 1)
    c.wire('XOR1', 'AND2', 0)
    c.wire('Cin', 'AND2', 1)
    c.wire('AND1', 'OR1', 0)
    c.wire('AND2', 'OR1', 1)
    return c


def run_truth_table(circuit, input_names):
    rows = []
    for i in range(2 ** len(input_names)):
        bits = [(i >> j) & 1 for j in range(len(input_names))]
        for j, name in enumerate(input_names):
            circuit.set_input(name, bool(bits[j]))
        rows.append(tuple(sorted(circuit.evaluate().items())))
    return tuple(rows)


class GoldenVectorTest(unittest.TestCase):
    def test_full_adder_golden(self):
        c = make_full_adder()
        rows = run_truth_table(c, ('A', 'B', 'Cin'))
        expected = (
            (('Carry', False), ('Sum', False)),
            (('Carry', False), ('Sum', True)),
            (('Carry', False), ('Sum', True)),
            (('Carry', True), ('Sum', False)),
            (('Carry', False), ('Sum', True)),
            (('Carry', True), ('Sum', False)),
            (('Carry', True), ('Sum', False)),
            (('Carry', True), ('Sum', True)),
        )
        self.assertEqual(rows, expected)

    def test_fanout_golden(self):
        c = Circuit('Fanout')
        c.add_gate('N1', 'NOT')
        c.add_gate('AND1', 'AND')
        c.add_gate('OR1', 'OR')
        c.add_input('A', False)
        c.add_output('Y', 'OR1')
        c.wire('A', 'N1', 0)
        c.wire('A', 'AND1', 0)
        c.wire('N1', 'AND1', 1)
        c.wire('AND1', 'OR1', 0)
        c.wire('A', 'OR1', 1)
        rows = run_truth_table(c, ('A',))
        self.assertEqual(rows,
                         ((('Y', False),), (('Y', True),)))

    def test_matches_reference_on_random_acyclic_circuits(self):
        rng = random.Random(1234)
        gate_types = ['AND', 'OR', 'NOT', 'NAND', 'NOR', 'XOR', 'XNOR']
        for _ in range(60):
            c = Circuit('random')
            n_gates = rng.randint(1, 10)
            n_inputs = rng.randint(1, 4)
            inputs = [f'I{i}' for i in range(n_inputs)]
            for inp in inputs:
                c.add_input(inp, False)

            order = []
            for i in range(n_gates):
                g = f'G{i}'
                c.add_gate(g, rng.choice(gate_types))
                order.append(g)

            for i, g in enumerate(order):
                gate = c.gates[g]
                available = list(inputs) + order[:i]
                for idx in range(len(gate.inputs)):
                    if not available:
                        break
                    dep = available[rng.randrange(len(available))]
                    c.wire(dep, g, idx)

            c.add_output('Z', order[-1])
            if rng.random() < 0.5:
                c.add_output('W2', order[0])

            for _ in range(6):
                for inp in inputs:
                    c.set_input(inp, rng.random() < 0.5)
                self.assertEqual(c.evaluate(),
                                 old_evaluate_greedy(c))


class TopoCacheTest(unittest.TestCase):
    def test_order_is_reused_across_evaluations(self):
        c = make_full_adder()
        c.evaluate()
        first = c._topo_order
        c.evaluate()
        self.assertIs(first, c._topo_order, "topo order must be memoized")

    def test_order_rebuilt_after_wire_change(self):
        c = make_full_adder()
        c.evaluate()
        first = c._topo_order
        c.add_gate('G1', 'NOT')
        self.assertIsNone(c._topo_order, "add_gate must invalidate cache")
        c.wire('A', 'G1', 0)
        self.assertIsNone(c._topo_order, "wire must invalidate cache")
        c.evaluate()
        second = c._topo_order
        self.assertIsNotNone(second)
        c.evaluate()
        self.assertIs(second, c._topo_order)

    def test_topological_property(self):
        c = make_full_adder()
        order = c._build_topo_order()
        position = {g: i for i, g in enumerate(order)}
        for src, dests in c.wires.items():
            for g, _ in dests:
                if src in c.gates and g in c.gates:
                    self.assertLess(position[src], position[g],
                                    f"{src} must precede {g}")


class CycleDetectionTest(unittest.TestCase):
    def test_self_loop_detected(self):
        c = Circuit('loop')
        c.add_gate('N1', 'NOT')
        c.add_input('A', False)
        c.wire('A', 'N1', 0)
        c.wire('N1', 'N1', 0)
        c.set_input('A', True)
        with self.assertRaises(CircuitError) as cm:
            c.evaluate()
        self.assertIn('N1', str(cm.exception))

    def test_multi_gate_cycle_detected(self):
        c = Circuit('mul')
        c.add_gate('G1', 'NOT')
        c.add_gate('G2', 'NOT')
        c.add_input('A', False)
        c.wire('A', 'G1', 0)
        c.wire('G1', 'G2', 0)
        c.wire('G2', 'G1', 0)
        c.set_input('A', True)
        with self.assertRaises(CircuitError) as cm:
            c.evaluate()
        self.assertIn('G1', str(cm.exception))
        self.assertIn('G2', str(cm.exception))


if __name__ == '__main__':
    unittest.main()