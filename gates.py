#!/usr/bin/env python3
"""
Logic Gates Simulator - Interactive digital logic circuit simulator
Author: Sagar Jadhav
"""

from collections import defaultdict, deque

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
        self._topo_order = None
    
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
        self._topo_order = None
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
        self.wires[from_node].append((to_gate, to_input_index))
        self._topo_order = None
    
    def _build_topo_order(self):
        """Kahn's algorithm: topological order of gates, memoized."""
        fan_in = defaultdict(set)
        fan_out = defaultdict(list)
        for src, dests in self.wires.items():
            for g, _ in dests:
                if g in self.gates:
                    fan_out[src].append(g)
                    if src in self.gates:
                        fan_in[g].add(src)

        in_degree = {g: len(fan_in[g]) for g in self.gates}
        ready = deque(g for g in self.gates if in_degree[g] == 0)
        order = []

        while ready:
            gate = ready.popleft()
            order.append(gate)
            for g in fan_out[gate]:
                if g in self.gates:
                    in_degree[g] -= 1
                    if in_degree[g] == 0:
                        ready.append(g)

        if len(order) < len(self.gates):
            cycle_gates = [g for g in self.gates if g not in order]
            raise CircuitError(f"Cycle detected involving gates: {', '.join(cycle_gates)}")

        self._topo_order = order
        return order
    
    def evaluate(self):
        if self._topo_order is None:
            self._build_topo_order()

        for gate in self.gates.values():
            gate.output = False
            for i in range(len(gate.inputs)):
                gate.inputs[i] = False

        for name, value in self.inputs.items():
            for gate, idx in self.wires[name]:
                self.gates[gate].set_input(idx, value)

        for name in self._topo_order:
            gate = self.gates[name]
            gate.evaluate()
            for g, idx in self.wires[name]:
                if g in self.gates:
                    self.gates[g].set_input(idx, gate.output)

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
