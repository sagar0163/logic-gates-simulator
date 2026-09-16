# Logic Gates Simulator

Interactive digital logic circuit simulator in Python.

A zero-dependency, `pip install`-able library for composing and verifying
digital circuits in scripts and tests.

## Features

- All basic gates: AND, OR, NOT, NAND, NOR, XOR, XNOR
- Custom circuit builder
- Truth table generator
- Built-in Half Adder and Full Adder circuits
- No third-party runtime dependencies

## Installation

```bash
pip install .
```

This installs the `logic_gates` package and the `logic-gates` console command.
The library remains importable from any directory (use a virtual environment
or `pip install --user .` as appropriate).

## Usage

### CLI

```bash
logic-gates            # run the built-in demos
python -m logic_gates  # same, module entry point
```

### Library

```python
from logic_gates import ANDGate, ORGate, NOTGate

and_gate = ANDGate()
and_gate.inputs = [True, False]
and_gate.evaluate()
print(and_gate.output)  # False
```

### Circuits

```python
from logic_gates import Circuit

adder = Circuit("Half Adder")
adder.add_gate("XOR1", "XOR")
adder.add_gate("AND1", "AND")
adder.add_input("A", False)
adder.add_input("B", False)
adder.add_output("Sum", "XOR1")
adder.add_output("Carry", "AND1")
adder.wire("A", "XOR1", 0)
adder.wire("B", "XOR1", 1)
adder.wire("A", "AND1", 0)
adder.wire("B", "AND1", 1)

adder.set_input("A", True)
adder.set_input("B", True)
print(adder.evaluate())  # {'Sum': False, 'Carry': True}
```

## Running from a source checkout

Backward-compatible shims remain in place:

```bash
python gates.py
from gates import ANDGate  # works in the repo root
```

## Tests

```bash
python -m unittest test_fan_out test_issue_2
```

## License

[MIT](LICENSE)

## Author

Sagar Jadhav