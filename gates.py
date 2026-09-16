#!/usr/bin/env python3
"""
Logic Gates Simulator - Interactive digital logic circuit simulator
Author: Sagar Jadhav
"""

import json
from collections import defaultdict

SERIALIZATION_FORMAT = "logic-gates-simulator"
SERIALIZATION_VERSION = 1
_JSON_KEYS = frozenset({"format", "version", "name", "inputs", "gates", "wires", "outputs"})
_WIRE_KEYS = frozenset({"from", "to_gate", "to_input"})

class Gate:
    """Base class for all logic gates"""
    def __init__(self, name, inputs=2):
        self.name = name
        self.inputs = [False] * inputs
        self.output = False
    
    def set_input(self, index, value):
        if 0 <= index < len(self.inputs):
            self.inputs[index] = value
    
    def get_output(self):
        return self.output

class ANDGate(Gate):
    def __init__(self):
        super().__init__("AND", 2)
    
    def evaluate(self):
        self.output = all(self.inputs)
        return self.output

class ORGate(Gate):
    def __init__(self):
        super().__init__("OR", 2)
    
    def evaluate(self):
        self.output = any(self.inputs)
        return self.output

class NOTGate(Gate):
    def __init__(self):
        super().__init__("NOT", 1)
    
    def evaluate(self):
        self.output = not self.inputs[0]
        return self.output

class NANDGate(Gate):
    def __init__(self):
        super().__init__("NAND", 2)
    
    def evaluate(self):
        self.output = not all(self.inputs)
        return self.output

class NORGate(Gate):
    def __init__(self):
        super().__init__("NOR", 2)
    
    def evaluate(self):
        self.output = not any(self.inputs)
        return self.output

class XORGate(Gate):
    def __init__(self):
        super().__init__("XOR", 2)
    
    def evaluate(self):
        self.output = self.inputs[0] ^ self.inputs[1]
        return self.output

class XNORGate(Gate):
    def __init__(self):
        super().__init__("XNOR", 2)
    
    def evaluate(self):
        self.output = not (self.inputs[0] ^ self.inputs[1])
        return self.output

class CircuitError(Exception):
    """Exception raised for errors in the circuit (e.g., wiring errors, cycles)."""
    pass

class Circuit:
    """Digital circuit simulator"""
    def __init__(self, name):
        self.name = name
        self.gates = {}
        self.wires = defaultdict(list)
        self.inputs = {}
        self.outputs = {}
    
    def add_gate(self, name, gate_type):
        gate_types = {
            'AND': ANDGate,
            'OR': ORGate,
            'NOT': NOTGate,
            'NAND': NANDGate,
            'NOR': NORGate,
            'XOR': XORGate,
            'XNOR': XNORGate,
        }
        if gate_type not in gate_types:
            raise CircuitError(f"Unknown gate type: '{gate_type}'")
        self.gates[name] = gate_types[gate_type]()
        return self.gates[name]
    
    def add_input(self, name, value=False):
        self.inputs[name] = value
    
    def add_output(self, name, source):
        self.outputs[name] = source
    
    def set_input(self, name, value):
        if name in self.inputs:
            self.inputs[name] = value
    
    def wire(self, from_node, to_gate, to_input_index):
        if from_node not in self.inputs and from_node not in self.gates:
            raise CircuitError(f"Unknown source node: '{from_node}'")
        if to_gate not in self.gates:
            raise CircuitError(f"Unknown destination gate: '{to_gate}'")
        gate = self.gates[to_gate]
        if not isinstance(to_input_index, int) or isinstance(to_input_index, bool):
            raise CircuitError(f"Invalid input index for gate '{to_gate}', not an integer")
        if to_input_index < 0 or to_input_index >= len(gate.inputs):
            raise CircuitError(
                f"Invalid input index {to_input_index} for gate '{to_gate}' ({gate.name})"
            )
        self.wires[from_node].append((to_gate, to_input_index))
    
    def evaluate(self):
        for gate in self.gates.values():
            gate.output = False
            for i in range(len(gate.inputs)):
                gate.inputs[i] = False

        for name, value in self.inputs.items():
            for gate, idx in self.wires[name]:
                self.gates[gate].set_input(idx, value)

        evaluated = set()
        while len(evaluated) < len(self.gates):
            progress = False
            for name, gate in self.gates.items():
                if name in evaluated:
                    continue
                ready = True
                for src, dests in self.wires.items():
                    for g, idx in dests:
                        if g == name:
                            if src in self.gates and src not in evaluated:
                                ready = False
                                break
                    if not ready:
                        break

                if ready:
                    gate.evaluate()
                    evaluated.add(name)
                    progress = True
                    for g, idx in self.wires[name]:
                        if g in self.gates:
                            self.gates[g].set_input(idx, gate.output)
            
            if not progress:
                cycle_gates = [g for g in self.gates if g not in evaluated]
                raise CircuitError(f"Cycle detected involving gates: {', '.join(cycle_gates)}")
        
        result = {}
        for name, source in self.outputs.items():
            if source in self.gates:
                result[name] = self.gates[source].output
        return result
    
    def print_truth_table(self, *input_names):
        print(f"\n{' | '.join(input_names)} | {' | '.join(self.outputs.keys())}")
        print('-' * (len(input_names) * 4 + len(self.outputs) * 4))
        
        for i in range(2 ** len(input_names)):
            bits = [(i >> j) & 1 for j in range(len(input_names))]
            for j, name in enumerate(input_names):
                self.set_input(name, bool(bits[j]))
            
            result = self.evaluate()
            row = ' | '.join(['✓' if b else '✗' for b in bits])
            out = ' | '.join(['✓' if result.get(k, False) else '✗' for k in self.outputs.keys()])
            print(f"{row} | {out}")

    def to_json(self, indent=2):
        """Serialize the circuit to a JSON string.

        The output is a plain, human-readable object with a stable schema:
        format/version markers, the circuit name, input/output names, the
        gate table, and a flat list of wires. Only booleans, strings, and
        integers are used, so it can be shared and diffed safely.
        """
        data = {
            "format": SERIALIZATION_FORMAT,
            "version": SERIALIZATION_VERSION,
            "name": self.name,
            "inputs": list(self.inputs.keys()),
            "gates": {name: gate.name for name, gate in self.gates.items()},
            "wires": [
                {"from": src, "to_gate": sink, "to_input": index}
                for src, sinks in self.wires.items()
                for sink, index in sinks
            ],
            "outputs": dict(self.outputs),
        }
        return json.dumps(data, indent=indent)

    @classmethod
    def from_json(cls, data):
        """Rebuild a Circuit from a JSON string or an already-parsed dict.

        Parsing is strict: only ``json.load``-produced objects are accepted,
        unknown top-level/wire keys are rejected, every reference must point
        at a real input/gate, and cyclic wiring is refused. No code is ever
        evaluated (no eval/exec/pickle, no attribute injection).
        """
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as exc:
                raise CircuitError(f"Malformed JSON: {exc}") from exc

        if not isinstance(data, dict):
            raise CircuitError(f"Expected a JSON object, got {type(data).__name__}")

        unknown = set(data) - _JSON_KEYS
        if unknown:
            raise CircuitError(f"Unknown key(s): {', '.join(sorted(unknown))}")
        missing = _JSON_KEYS - set(data)
        if missing:
            raise CircuitError(f"Missing key(s): {', '.join(sorted(missing))}")

        if data["format"] != SERIALIZATION_FORMAT:
            raise CircuitError(f"Unsupported format: '{data['format']}'")
        if not isinstance(data["version"], int) or isinstance(data["version"], bool):
            raise CircuitError(f"Unsupported version: {data['version']!r}")
        if data["version"] != SERIALIZATION_VERSION:
            raise CircuitError(f"Unsupported version: {data['version']!r}")
        if not isinstance(data["name"], str):
            raise CircuitError("'name' must be a string")
        if not isinstance(data["inputs"], list) or not all(
            isinstance(i, str) for i in data["inputs"]
        ):
            raise CircuitError("'inputs' must be a list of strings")
        if not isinstance(data["gates"], dict) or any(
            not isinstance(k, str) or not isinstance(v, str)
            for k, v in data["gates"].items()
        ):
            raise CircuitError("'gates' must map gate names to gate type strings")
        if not isinstance(data["wires"], list):
            raise CircuitError("'wires' must be a list")
        if not isinstance(data["outputs"], dict) or any(
            not isinstance(k, str) or not isinstance(v, str)
            for k, v in data["outputs"].items()
        ):
            raise CircuitError("'outputs' must map output names to gate names")

        circuit = cls(data["name"])

        for input_name in data["inputs"]:
            circuit.add_input(input_name)

        for gate_name, gate_type in data["gates"].items():
            circuit.add_gate(gate_name, gate_type)

        for wire in data["wires"]:
            if not isinstance(wire, dict):
                raise CircuitError("Each wire must be an object")
            unknown_wire = set(wire) - _WIRE_KEYS
            if unknown_wire:
                raise CircuitError(f"Unknown wire key(s): {', '.join(sorted(unknown_wire))}")
            missing_wire = _WIRE_KEYS - set(wire)
            if missing_wire:
                raise CircuitError(f"Wire missing key(s): {', '.join(sorted(missing_wire))}")
            if not isinstance(wire["from"], str) or not isinstance(wire["to_gate"], str):
                raise CircuitError("Wire 'from' and 'to_gate' must be strings")
            circuit.wire(wire["from"], wire["to_gate"], wire["to_input"])

        for output_name, source in data["outputs"].items():
            if source not in circuit.gates:
                raise CircuitError(
                    f"Output '{output_name}' references unknown gate: '{source}'"
                )
            circuit.add_output(output_name, source)

        cycle_gates = circuit._detect_cycle_gates()
        if cycle_gates:
            raise CircuitError(
                f"Cycle detected involving gates: {', '.join(cycle_gates)}"
            )

        return circuit

    def _detect_cycle_gates(self):
        """Return the list of gates trapped in a wiring cycle (empty if none)."""
        children = defaultdict(list)
        indegree = {name: 0 for name in self.gates}
        for src, sinks in self.wires.items():
            if src not in self.gates:
                continue
            for sink, _index in sinks:
                if sink in self.gates:
                    children[src].append(sink)
                    indegree[sink] += 1

        queue = [name for name in self.gates if indegree[name] == 0]
        removed = set(queue)
        while queue:
            current = queue.pop(0)
            for child in children[current]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)
                    removed.add(child)
        return [name for name in self.gates if name not in removed]


def load_circuit(filename):
    """Load a Circuit from a JSON file using strict validation."""
    with open(filename, encoding="utf-8") as handle:
        return Circuit.from_json(json.load(handle))


def save_circuit(circuit, filename, indent=2):
    """Save a Circuit to a JSON file as human-readable text."""
    with open(filename, "w", encoding="utf-8") as handle:
        handle.write(circuit.to_json(indent=indent))
        handle.write("\n")

def demo_basic_gates():
    print("=" * 50)
    print("LOGIC GATES TRUTH TABLES")
    print("=" * 50)
    
    gates = [ANDGate(), ORGate(), NANDGate(), NORGate(), XORGate(), XNORGate(), NOTGate()]
    
    for gate in gates:
        print(f"\n{gate.name} Gate:")
        print("A | B | Output")
        print("-" * 15)
        
        if len(gate.inputs) == 2:
            for a in [False, True]:
                for b in [False, True]:
                    gate.inputs[0] = a
                    gate.inputs[1] = b
                    gate.evaluate()
                    print(f"{'✓' if a else '✗'} | {'✓' if b else '✗'} | {'✓' if gate.output else '✗'}")
        else:
            for a in [False, True]:
                gate.inputs[0] = a
                gate.evaluate()
                print(f"{'✓' if a else '✗'} | {'✓' if gate.output else '✗'}")

def demo_circuit():
    print("\n" + "=" * 50)
    print("HALF ADDER CIRCUIT")
    print("=" * 50)
    
    circuit = Circuit("Half Adder")
    circuit.add_gate('XOR1', 'XOR')
    circuit.add_gate('AND1', 'AND')
    circuit.add_input('A', False)
    circuit.add_input('B', False)
    circuit.add_output('Sum', 'XOR1')
    circuit.add_output('Carry', 'AND1')
    circuit.wire('A', 'XOR1', 0)
    circuit.wire('B', 'XOR1', 1)
    circuit.wire('A', 'AND1', 0)
    circuit.wire('B', 'AND1', 1)
    
    circuit.print_truth_table('A', 'B')

def demo_full_adder():
    print("\n" + "=" * 50)
    print("FULL ADDER CIRCUIT")
    print("=" * 50)
    
    circuit = Circuit("Full Adder")
    circuit.add_gate('XOR1', 'XOR')
    circuit.add_gate('XOR2', 'XOR')
    circuit.add_gate('AND1', 'AND')
    circuit.add_gate('AND2', 'AND')
    circuit.add_gate('OR1', 'OR')
    circuit.add_input('A', False)
    circuit.add_input('B', False)
    circuit.add_input('Cin', False)
    circuit.add_output('Sum', 'XOR2')
    circuit.add_output('Carry', 'OR1')
    circuit.wire('A', 'XOR1', 0)
    circuit.wire('B', 'XOR1', 1)
    circuit.wire('Cin', 'XOR2', 1)
    circuit.wire('XOR1', 'XOR2', 0)
    circuit.wire('A', 'AND1', 0)
    circuit.wire('B', 'AND1', 1)
    circuit.wire('XOR1', 'AND2', 0)
    circuit.wire('Cin', 'AND2', 1)
    circuit.wire('AND1', 'OR1', 0)
    circuit.wire('AND2', 'OR1', 1)
    
    circuit.print_truth_table('A', 'B', 'Cin')

if __name__ == '__main__':
    demo_basic_gates()
    demo_circuit()
    demo_full_adder()
