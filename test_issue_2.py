import unittest
from logic_gates import Circuit, CircuitError

class TestIssue2(unittest.TestCase):
    def test_cycle_detection(self):
        c = Circuit('loop')
        c.add_gate('N1', 'NOT')
        c.add_input('A', False)
        c.wire('A', 'N1', 0)
        c.wire('N1', 'N1', 0)
        c.set_input('A', True)
        with self.assertRaises(CircuitError) as context:
            c.evaluate()
        self.assertIn("Cycle detected involving gates: N1", str(context.exception))

    def test_invalid_gate_type(self):
        c = Circuit('invalid_gate')
        with self.assertRaisesRegex(CircuitError, "Unknown gate type: 'UNKNOWN'"):
            c.add_gate('G1', 'UNKNOWN')

    def test_invalid_wiring_source(self):
        c = Circuit('invalid_wiring_src')
        c.add_gate('G1', 'NOT')
        with self.assertRaisesRegex(CircuitError, "Unknown source node: 'UNKNOWN'"):
            c.wire('UNKNOWN', 'G1', 0)

    def test_invalid_wiring_dest(self):
        c = Circuit('invalid_wiring_dest')
        c.add_input('A', False)
        with self.assertRaisesRegex(CircuitError, "Unknown destination gate: 'UNKNOWN'"):
            c.wire('A', 'UNKNOWN', 0)

if __name__ == '__main__':
    unittest.main()
