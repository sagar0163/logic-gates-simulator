"""Entry point for python -m logic_gates"""
from logic_gates import demo_basic_gates, demo_circuit, demo_full_adder

def main():
    demo_basic_gates()
    demo_circuit()
    demo_full_adder()

if __name__ == "__main__":
    main()
