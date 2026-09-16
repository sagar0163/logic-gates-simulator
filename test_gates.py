import unittest
import io
import sys
from gates import Circuit, ANDGate, ORGate, NOTGate, NANDGate, NORGate, XORGate, XNORGate, CircuitError

class TestBasicGates(unittest.TestCase):
    def test_and_gate(self):
        c = Circuit("Test AND")
        c.add_gate("G1", "AND")
        c.add_input("A")
        c.add_input("B")
        c.add_output("Out", "G1")
        c.wire("A", "G1", 0)
        c.wire("B", "G1", 1)
        
        truths = [(False, False, False), (False, True, False), (True, False, False), (True, True, True)]
        for a, b, out in truths:
            c.set_input("A", a)
            c.set_input("B", b)
            res = c.evaluate()
            self.assertEqual(res["Out"], out, f"AND failed for {a}, {b}")

    def test_or_gate(self):
        c = Circuit("Test OR")
        c.add_gate("G1", "OR")
        c.add_input("A")
        c.add_input("B")
        c.add_output("Out", "G1")
        c.wire("A", "G1", 0)
        c.wire("B", "G1", 1)
        
        truths = [(False, False, False), (False, True, True), (True, False, True), (True, True, True)]
        for a, b, out in truths:
            c.set_input("A", a)
            c.set_input("B", b)
            res = c.evaluate()
            self.assertEqual(res["Out"], out, f"OR failed for {a}, {b}")

    def test_not_gate(self):
        c = Circuit("Test NOT")
        c.add_gate("G1", "NOT")
        c.add_input("A")
        c.add_output("Out", "G1")
        c.wire("A", "G1", 0)
        
        truths = [(False, True), (True, False)]
        for a, out in truths:
            c.set_input("A", a)
            res = c.evaluate()
            self.assertEqual(res["Out"], out, f"NOT failed for {a}")

    def test_nand_gate(self):
        c = Circuit("Test NAND")
        c.add_gate("G1", "NAND")
        c.add_input("A")
        c.add_input("B")
        c.add_output("Out", "G1")
        c.wire("A", "G1", 0)
        c.wire("B", "G1", 1)
        
        truths = [(False, False, True), (False, True, True), (True, False, True), (True, True, False)]
        for a, b, out in truths:
            c.set_input("A", a)
            c.set_input("B", b)
            res = c.evaluate()
            self.assertEqual(res["Out"], out, f"NAND failed for {a}, {b}")

    def test_nor_gate(self):
        c = Circuit("Test NOR")
        c.add_gate("G1", "NOR")
        c.add_input("A")
        c.add_input("B")
        c.add_output("Out", "G1")
        c.wire("A", "G1", 0)
        c.wire("B", "G1", 1)
        
        truths = [(False, False, True), (False, True, False), (True, False, False), (True, True, False)]
        for a, b, out in truths:
            c.set_input("A", a)
            c.set_input("B", b)
            res = c.evaluate()
            self.assertEqual(res["Out"], out, f"NOR failed for {a}, {b}")

    def test_xor_gate(self):
        c = Circuit("Test XOR")
        c.add_gate("G1", "XOR")
        c.add_input("A")
        c.add_input("B")
        c.add_output("Out", "G1")
        c.wire("A", "G1", 0)
        c.wire("B", "G1", 1)
        
        truths = [(False, False, False), (False, True, True), (True, False, True), (True, True, False)]
        for a, b, out in truths:
            c.set_input("A", a)
            c.set_input("B", b)
            res = c.evaluate()
            self.assertEqual(res["Out"], out, f"XOR failed for {a}, {b}")

    def test_xnor_gate(self):
        c = Circuit("Test XNOR")
        c.add_gate("G1", "XNOR")
        c.add_input("A")
        c.add_input("B")
        c.add_output("Out", "G1")
        c.wire("A", "G1", 0)
        c.wire("B", "G1", 1)
        
        truths = [(False, False, True), (False, True, False), (True, False, False), (True, True, True)]
        for a, b, out in truths:
            c.set_input("A", a)
            c.set_input("B", b)
            res = c.evaluate()
            self.assertEqual(res["Out"], out, f"XNOR failed for {a}, {b}")


class TestAdders(unittest.TestCase):
    def test_half_adder(self):
        c = Circuit("Half Adder")
        c.add_gate("XOR1", "XOR")
        c.add_gate("AND1", "AND")
        c.add_input("A")
        c.add_input("B")
        c.add_output("Sum", "XOR1")
        c.add_output("Carry", "AND1")
        c.wire("A", "XOR1", 0)
        c.wire("B", "XOR1", 1)
        c.wire("A", "AND1", 0)
        c.wire("B", "AND1", 1)
        
        truths = [
            (False, False, False, False),
            (False, True, True, False),
            (True, False, True, False),
            (True, True, False, True)
        ]
        for a, b, sum_val, carry_val in truths:
            c.set_input("A", a)
            c.set_input("B", b)
            res = c.evaluate()
            self.assertEqual(res["Sum"], sum_val)
            self.assertEqual(res["Carry"], carry_val)

    def test_full_adder(self):
        c = Circuit("Full Adder")
        c.add_gate("XOR1", "XOR")
        c.add_gate("XOR2", "XOR")
        c.add_gate("AND1", "AND")
        c.add_gate("AND2", "AND")
        c.add_gate("OR1", "OR")
        c.add_input("A")
        c.add_input("B")
        c.add_input("Cin")
        c.add_output("Sum", "XOR2")
        c.add_output("Carry", "OR1")
        c.wire("A", "XOR1", 0)
        c.wire("B", "XOR1", 1)
        c.wire("Cin", "XOR2", 1)
        c.wire("XOR1", "XOR2", 0)
        c.wire("A", "AND1", 0)
        c.wire("B", "AND1", 1)
        c.wire("XOR1", "AND2", 0)
        c.wire("Cin", "AND2", 1)
        c.wire("AND1", "OR1", 0)
        c.wire("AND2", "OR1", 1)

        truths = [
            (False, False, False, False, False),
            (False, False, True, True, False),
            (False, True, False, True, False),
            (False, True, True, False, True),
            (True, False, False, True, False),
            (True, False, True, False, True),
            (True, True, False, False, True),
            (True, True, True, True, True),
        ]
        for a, b, cin, sum_val, carry_val in truths:
            c.set_input("A", a)
            c.set_input("B", b)
            c.set_input("Cin", cin)
            res = c.evaluate()
            self.assertEqual(res["Sum"], sum_val)
            self.assertEqual(res["Carry"], carry_val)


class TestCircuitFeatures(unittest.TestCase):
    def test_fan_out(self):
        c = Circuit("Fan-out")
        c.add_gate("AND1", "AND")
        c.add_gate("OR1", "OR")
        c.add_input("A")
        c.add_input("B")
        c.add_output("Out1", "AND1")
        c.add_output("Out2", "OR1")
        
        c.wire("A", "AND1", 0)
        c.wire("A", "OR1", 0)
        c.wire("B", "AND1", 1)
        c.wire("B", "OR1", 1)
        
        c.set_input("A", True)
        c.set_input("B", False)
        res = c.evaluate()
        self.assertFalse(res["Out1"])
        self.assertTrue(res["Out2"])

    def test_cycle_detection(self):
        c = Circuit("Cycle")
        c.add_gate("NOT1", "NOT")
        c.add_gate("NOT2", "NOT")
        c.wire("NOT1", "NOT2", 0)
        c.wire("NOT2", "NOT1", 0)
        
        with self.assertRaises(CircuitError):
            c.evaluate()

    def test_truth_table_generation(self):
        c = Circuit("Half Adder")
        c.add_gate("XOR1", "XOR")
        c.add_gate("AND1", "AND")
        c.add_input("A")
        c.add_input("B")
        c.add_output("Sum", "XOR1")
        c.add_output("Carry", "AND1")
        c.wire("A", "XOR1", 0)
        c.wire("B", "XOR1", 1)
        c.wire("A", "AND1", 0)
        c.wire("B", "AND1", 1)
        
        captured_output = io.StringIO()
        sys.stdout = captured_output
        c.print_truth_table("A", "B")
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        self.assertIn("A | B | Sum | Carry", output)
        self.assertIn("✗ | ✗ | ✗ | ✗", output)
        self.assertIn("✗ | ✓ | ✓ | ✗", output)
        self.assertIn("✓ | ✗ | ✓ | ✗", output)
        self.assertIn("✓ | ✓ | ✗ | ✓", output)

if __name__ == "__main__":
    unittest.main()
