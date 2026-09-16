#!/usr/bin/env python3
"""
Logic Gates Simulator - Interactive digital logic circuit simulator

Backward-compatible shim: this module re-exports everything from the
`logic_gates` package so that `from gates import ANDGate` keeps working.

Author: Sagar Jadhav
"""

from logic_gates import (
    ANDGate,
    ORGate,
    NOTGate,
    NANDGate,
    NORGate,
    XORGate,
    XNORGate,
    Gate,
    Circuit,
    CircuitError,
    __version__,
    demo_basic_gates,
    demo_circuit,
    demo_full_adder,
)

__all__ = [
    "ANDGate",
    "ORGate",
    "NOTGate",
    "NANDGate",
    "NORGate",
    "XORGate",
    "XNORGate",
    "Gate",
    "Circuit",
    "CircuitError",
    "__version__",
    "demo_basic_gates",
    "demo_circuit",
    "demo_full_adder",
]

if __name__ == "__main__":
    demo_basic_gates()
    demo_circuit()
    demo_full_adder()