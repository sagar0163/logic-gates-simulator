#!/usr/bin/env python3
"""Serialization tests for Issue #7: strict-validated JSON save/load."""

import json

import pytest

import gates
from gates import Circuit, CircuitError


def circuit_rows(circuit):
    """Evaluate a circuit over every input combination and return the rows."""
    input_names = list(circuit.inputs)
    rows = []
    for i in range(2 ** len(input_names)):
        bits = [(i >> j) & 1 for j in range(len(input_names))]
        for j, name in enumerate(input_names):
            circuit.set_input(name, bool(bits[j]))
        rows.append(circuit.evaluate())
    return rows


def single_gate_circuit(gate_type, num_inputs):
    circuit = Circuit(gate_type)
    gate_name = "G1"
    circuit.add_gate(gate_name, gate_type)
    for i in range(num_inputs):
        circuit.add_input(f"I{i}")
        circuit.wire(f"I{i}", gate_name, i)
    circuit.add_output("Out", gate_name)
    return circuit


GATE_INPUTS = {"AND": 2, "OR": 2, "NOT": 1, "NAND": 2, "NOR": 2, "XOR": 2, "XNOR": 2}


def make_half_adder():
    circuit = Circuit("Half Adder")
    circuit.name = "Half Adder"
    circuit.add_gate("XOR1", "XOR")
    circuit.add_gate("AND1", "AND")
    circuit.add_input("A", False)
    circuit.add_input("B", False)
    circuit.add_output("Sum", "XOR1")
    circuit.add_output("Carry", "AND1")
    circuit.wire("A", "XOR1", 0)
    circuit.wire("B", "XOR1", 1)
    circuit.wire("A", "AND1", 0)
    circuit.wire("B", "AND1", 1)
    return circuit


def make_full_adder():
    circuit = Circuit("Full Adder")
    circuit.name = "Full Adder"
    circuit.add_gate("XOR1", "XOR")
    circuit.add_gate("XOR2", "XOR")
    circuit.add_gate("AND1", "AND")
    circuit.add_gate("AND2", "AND")
    circuit.add_gate("OR1", "OR")
    circuit.add_input("A", False)
    circuit.add_input("B", False)
    circuit.add_input("Cin", False)
    circuit.add_output("Sum", "XOR2")
    circuit.add_output("Carry", "OR1")
    circuit.wire("A", "XOR1", 0)
    circuit.wire("B", "XOR1", 1)
    circuit.wire("Cin", "XOR2", 1)
    circuit.wire("XOR1", "XOR2", 0)
    circuit.wire("A", "AND1", 0)
    circuit.wire("B", "AND1", 1)
    circuit.wire("XOR1", "AND2", 0)
    circuit.wire("Cin", "AND2", 1)
    circuit.wire("AND1", "OR1", 0)
    circuit.wire("AND2", "OR1", 1)
    return circuit


def assert_round_trip(circuit):
    restored = Circuit.from_json(circuit.to_json())
    assert restored.name == circuit.name
    assert list(restored.inputs) == list(circuit.inputs)
    assert restored.outputs == circuit.outputs
    assert dict(restored.wires) == dict(circuit.wires)
    assert circuit_rows(restored) == circuit_rows(circuit)


class TestRoundTrip:
    def test_each_gate_type(self):
        for gate_type, num_inputs in GATE_INPUTS.items():
            assert_round_trip(single_gate_circuit(gate_type, num_inputs))

    def test_half_adder(self):
        assert_round_trip(make_half_adder())

    def test_full_adder(self):
        assert_round_trip(make_full_adder())

    def test_to_json_is_text_json(self):
        text = make_half_adder().to_json()
        assert isinstance(text, str)
        parsed = json.loads(text)
        assert parsed["format"] == gates.SERIALIZATION_FORMAT
        assert parsed["version"] == gates.SERIALIZATION_VERSION

    def test_from_json_accepts_parsed_dict(self):
        data = json.loads(make_half_adder().to_json())
        restored = Circuit.from_json(data)
        assert circuit_rows(restored) == circuit_rows(make_half_adder())


class TestStrictValidation:
    def test_truncated_json_raises(self):
        truncated = '{"format": "logic-gates-simulator", "version": 1, "name": "x", "inputs": ['
        with pytest.raises(CircuitError, match="Malformed JSON"):
            Circuit.from_json(truncated)

    def test_non_object_root_raises(self):
        with pytest.raises(CircuitError, match="Expected a JSON object"):
            Circuit.from_json("[1, 2, 3]")

    def test_unknown_top_level_key_raises(self):
        data = json.loads(make_half_adder().to_json())
        data["evil_attr"] = {"__class__": "x"}
        with pytest.raises(CircuitError, match="Unknown key"):
            Circuit.from_json(data)

    def test_missing_key_raises(self):
        data = json.loads(make_half_adder().to_json())
        del data["wires"]
        with pytest.raises(CircuitError, match="Missing key"):
            Circuit.from_json(data)

    def test_unknown_gate_type_raises(self):
        data = json.loads(make_half_adder().to_json())
        data["gates"]["EVIL"] = "__import__('os').system"
        with pytest.raises(CircuitError, match="Unknown gate type"):
            Circuit.from_json(data)

    def test_wire_to_nonexistent_gate_raises(self):
        data = json.loads(make_half_adder().to_json())
        data["wires"].append({"from": "A", "to_gate": "NOPE", "to_input": 0})
        with pytest.raises(CircuitError, match="Unknown destination gate"):
            Circuit.from_json(data)

    def test_wire_from_nonexistent_source_raises(self):
        data = json.loads(make_half_adder().to_json())
        data["wires"].append({"from": "NOPE", "to_gate": "XOR1", "to_input": 0})
        with pytest.raises(CircuitError, match="Unknown source node"):
            Circuit.from_json(data)

    def test_output_to_nonexistent_gate_raises(self):
        data = json.loads(make_half_adder().to_json())
        data["outputs"]["Broken"] = "NOPE"
        with pytest.raises(CircuitError, match="references unknown gate"):
            Circuit.from_json(data)

    def test_cyclic_wire_raises_on_load(self):
        data = json.loads(make_half_adder().to_json())
        data["gates"]["N1"] = "NOT"
        data["wires"].append({"from": "N1", "to_gate": "N1", "to_input": 0})
        with pytest.raises(CircuitError, match="Cycle detected"):
            Circuit.from_json(data)

    def test_indirect_cycle_raises_on_load(self):
        data = json.loads(make_half_adder().to_json())
        data["gates"]["G2"] = "NOT"
        data["wires"].append({"from": "AND1", "to_gate": "G2", "to_input": 0})
        data["wires"].append({"from": "G2", "to_gate": "AND1", "to_input": 0})
        with pytest.raises(CircuitError, match="Cycle detected"):
            Circuit.from_json(data)

    def test_unknown_wire_key_raises(self):
        data = json.loads(make_half_adder().to_json())
        data["wires"][0]["inject"] = {"__class__": "x"}
        with pytest.raises(CircuitError, match="Unknown wire key"):
            Circuit.from_json(data)

    def test_wire_missing_key_raises(self):
        data = json.loads(make_half_adder().to_json())
        del data["wires"][0]["to_gate"]
        with pytest.raises(CircuitError, match="Wire missing key"):
            Circuit.from_json(data)

    def test_out_of_range_input_index_raises(self):
        data = json.loads(make_half_adder().to_json())
        data["wires"].append({"from": "A", "to_gate": "XOR1", "to_input": 5})
        with pytest.raises(CircuitError, match="Invalid input index"):
            Circuit.from_json(data)

    def test_wrong_types_raise(self):
        data = json.loads(make_half_adder().to_json())
        data["name"] = 123
        with pytest.raises(CircuitError, match="'name' must be a string"):
            Circuit.from_json(data)

        data = json.loads(make_half_adder().to_json())
        data["inputs"] = "A"
        with pytest.raises(CircuitError, match="'inputs' must be a list"):
            Circuit.from_json(data)

        data = json.loads(make_half_adder().to_json())
        data["gates"] = []
        with pytest.raises(CircuitError, match="'gates' must map"):
            Circuit.from_json(data)

        data = json.loads(make_half_adder().to_json())
        data["wires"] = {}
        with pytest.raises(CircuitError, match="'wires' must be a list"):
            Circuit.from_json(data)

        data = json.loads(make_half_adder().to_json())
        data["wires"][0]["to_input"] = "0"
        with pytest.raises(CircuitError, match="Invalid input index"):
            Circuit.from_json(data)

    def test_filesystem_helpers_round_trip(self, tmp_path):
        path = tmp_path / "half_adder.json"
        gates.save_circuit(make_half_adder(), str(path))
        restored = gates.load_circuit(str(path))
        assert circuit_rows(restored) == circuit_rows(make_half_adder())


class TestNoEvalInLoadPath:
    def test_grep_eval_exec_pickle_absent(self):
        """Grep-check regression: no eval(/exec(/pickle anywhere in gates.py."""
        with open("gates.py", encoding="utf-8") as handle:
            source = handle.read()
        assert "eval(" not in source, "eval( found in gates.py"
        assert "exec(" not in source, "exec( found in gates.py"
        assert "pickle" not in source, "pickle found in gates.py"
        assert "setattr" not in source, "setattr found in gates.py"


if __name__ == "__main__":
    pytest.main([__file__])