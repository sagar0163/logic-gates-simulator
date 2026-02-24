#!/usr/bin/env python3
"""
Logic Gates Simulator - Interactive digital logic circuit simulator
Author: Sagar Jadhav
"""

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

class Circuit:
    """Digital circuit simulator"""
    def __init__(self, name):
        self.name = name
        self.gates = {}
        self.wires = {}
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
        self.wires[from_node] = (to_gate, to_input_index)
    
    def evaluate(self):
        for gate in self.gates.values():
            gate.output = False
        
        for name, value in self.inputs.items():
            if name in self.wires:
                gate, idx = self.wires[name]
                self.gates[gate].set_input(idx, value)
        
        evaluated = set()
        while len(evaluated) < len(self.gates):
            for name, gate in self.gates.items():
                if name in evaluated:
                    continue
                ready = True
                for i, inp in enumerate(gate.inputs):
                    for src, (g, idx) in self.wires.items():
                        if g == name and idx == i:
                            if src in self.gates and src not in evaluated:
                                ready = False
                                break
                
                if ready:
                    gate.evaluate()
                    evaluated.add(name)
        
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
