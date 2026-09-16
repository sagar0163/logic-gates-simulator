#!/usr/bin/env python3
"""Regression test for Issue #1: wire() must support fan-out.

A single source driving multiple gate inputs must not silently overwrite
previous wires. This test fails on the buggy dict-based wiring.
"""

import unittest

from gates import Circuit


class FanOutTest(unittest.TestCase):
    def test_single_source_drives_two_sinks(self):
        c = Circuit("Fan-out test")
        c.add_gate("AND1", "AND")
        c.add_gate("AND2", "AND")
        c.add_input("A", False)
        c.add_input("B", False)
        c.add_input("C", False)
        c.add_output("Out1", "AND1")
        c.add_output("Out2", "AND2")

        c.wire("A", "AND1", 0)
        c.wire("A", "AND2", 0)
        c.wire("B", "AND1", 1)
        c.wire("C", "AND2", 1)

        c.set_input("A", True)
        c.set_input("B", True)
        c.set_input("C", True)
        result = c.evaluate()

        self.assertTrue(result["Out1"], "AND1 should receive A=1")
        self.assertTrue(result["Out2"], "AND2 should receive A=1")

    def test_half_adder(self):
        c = Circuit("Half Adder")
        c.add_gate("XOR1", "XOR")
        c.add_gate("AND1", "AND")
        c.add_input("A", False)
        c.add_input("B", False)
        c.add_output("Sum", "XOR1")
        c.add_output("Carry", "AND1")
        c.wire("A", "XOR1", 0)
        c.wire("B", "XOR1", 1)
        c.wire("A", "AND1", 0)
        c.wire("B", "AND1", 1)

        for a in (False, True):
            for b in (False, True):
                c.set_input("A", a)
                c.set_input("B", b)
                result = c.evaluate()
                self.assertEqual(result["Sum"], a ^ b, f"Sum for A={a},B={b}")
                self.assertEqual(result["Carry"], a and b, f"Carry for A={a},B={b}")

    def test_full_adder(self):
        c = Circuit("Full Adder")
        c.add_gate("XOR1", "XOR")
        c.add_gate("XOR2", "XOR")
        c.add_gate("AND1", "AND")
        c.add_gate("AND2", "AND")
        c.add_gate("OR1", "OR")
        c.add_input("A", False)
        c.add_input("B", False)
        c.add_input("Cin", False)
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

        for a in (False, True):
            for b in (False, True):
                for cin in (False, True):
                    c.set_input("A", a)
                    c.set_input("B", b)
                    c.set_input("Cin", cin)
                    result = c.evaluate()
                    self.assertEqual(result["Sum"], a ^ b ^ cin,
                                     f"Sum for A={a},B={b},Cin={cin}")
                    self.assertEqual(result["Carry"], (a and b) or (a and cin) or (b and cin),
                                     f"Carry for A={a},B={b},Cin={cin}")


if __name__ == "__main__":
    unittest.main()