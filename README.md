# Logic Gates Simulator

Interactive digital logic circuit simulator in Python.

## Features

- All basic gates: AND, OR, NOT, NAND, NOR, XOR, XNOR
- Custom circuit builder
- Truth table generator
- Built-in Half Adder and Full Adder circuits

## Usage

```bash
python gates.py
```

## Gate Operations

```python
from gates import ANDGate, ORGate, NOTGate

and_gate = ANDGate()
and_gate.inputs = [True, False]
and_gate.evaluate()
print(and_gate.output)  # False
```

## Author

Sagar Jadhav
# Updated
