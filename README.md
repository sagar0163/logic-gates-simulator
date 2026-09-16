# Logic Gates Simulator

A static digital logic circuit simulator demonstration in Python.

## Features

- All basic gates: AND, OR, NOT, NAND, NOR, XOR, XNOR
- Built-in Half Adder and Full Adder circuits

## Installation

```bash
pip install .
```
*(Or use `pip install -e .` for an editable development install)*

## Usage

You can run the built-in demonstration script:

```bash
python gates.py
```

## Gate Operations

```python
from logic_gates.gates import ANDGate, ORGate, NOTGate

and_gate = ANDGate()
and_gate.inputs = [True, False]
and_gate.evaluate()
print(and_gate.output)  # False
```

## Author

Sagar Jadhav
