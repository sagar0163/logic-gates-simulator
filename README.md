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

## Save & Load Circuits (JSON)

Circuits serialize to a plain, human-readable JSON format (versioned, no
code, safe to share and diff). Loading is **strict** — malformed input raises
`CircuitError`; no code is ever executed.

```python
import gates
from gates import Circuit

c = Circuit("My design")
c.add_gate("N1", "NOT")
c.add_input("A")
c.add_output("Out", "N1")
c.wire("A", "N1", 0)

gates.save_circuit(c, "my_design.json")   # write to disk
restored = gates.load_circuit("my_design.json")  # read back (strict)
```

You can also go through strings or plain dicts:

```python
text = c.to_json()                 # -> JSON string
same_circuit = Circuit.from_json(text)   # parses a string...
same_circuit = Circuit.from_json({"format": ...})  # ...or an already-parsed dict
```

### Format

```json
{
  "format": "logic-gates-simulator",
  "version": 1,
  "name": "Half Adder",
  "inputs": ["A", "B"],
  "gates": { "XOR1": "XOR", "AND1": "AND" },
  "wires": [
    { "from": "A", "to_gate": "XOR1", "to_input": 0 },
    { "from": "A", "to_gate": "AND1", "to_input": 0 }
  ],
  "outputs": { "Sum": "XOR1", "Carry": "AND1" }
}
```

| Key        | Type             | Meaning                                        |
| ---------- | ---------------- | ---------------------------------------------- |
| `format`   | `"logic-gates-simulator"` | Format marker (must match exactly).    |
| `version`  | int              | Schema version (currently `1`).                 |
| `name`     | string           | Circuit name.                                   |
| `inputs`   | list of strings  | External input pins.                            |
| `gates`    | object           | Gate name → type (`AND`, `OR`, `NOT`, `NAND`, `NOR`, `XOR`, `XNOR`). |
| `wires`    | list of objects  | Each: `from` (input or gate), `to_gate`, `to_input` (0-based pin). |
| `outputs`  | object           | Output name → source gate.                      |

Validation on load: unknown keys/fields are rejected, every `from`/`to_gate`
must reference a real input/gate, wire pin indices must be in range, and
cyclic wiring raises `CircuitError`. See `examples/half_adder.json`.

## Demos

- Interactive run: `python gates.py` (basic gates, Half Adder, Full Adder)
- Load the shipped example and print its truth table:

```python
import gates

c = gates.load_circuit("examples/half_adder.json")
c.print_truth_table("A", "B")
```

## Tests

```bash
python3 -m pytest -q
```

## Author

Sagar Jadhav
