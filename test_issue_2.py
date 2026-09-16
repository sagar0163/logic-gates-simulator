import pytest
from gates import Circuit, CircuitError

def test_cycle_detection():
    c = Circuit('loop')
    c.add_gate('N1', 'NOT')
    c.add_input('A', False)
    c.wire('A', 'N1', 0)
    c.wire('N1', 'N1', 0)
    c.set_input('A', True)
    with pytest.raises(CircuitError) as excinfo:
        c.evaluate()
    assert "Cycle detected involving gates: N1" in str(excinfo.value)

def test_invalid_gate_type():
    c = Circuit('invalid_gate')
    with pytest.raises(CircuitError, match="Unknown gate type: 'UNKNOWN'"):
        c.add_gate('G1', 'UNKNOWN')

def test_invalid_wiring_source():
    c = Circuit('invalid_wiring_src')
    c.add_gate('G1', 'NOT')
    with pytest.raises(CircuitError, match="Unknown source node: 'UNKNOWN'"):
        c.wire('UNKNOWN', 'G1', 0)

def test_invalid_wiring_dest():
    c = Circuit('invalid_wiring_dest')
    c.add_input('A', False)
    with pytest.raises(CircuitError, match="Unknown destination gate: 'UNKNOWN'"):
        c.wire('A', 'UNKNOWN', 0)
