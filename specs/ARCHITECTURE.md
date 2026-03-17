# Architecture Document: Logic Gates Simulator

## 1. System Overview

Logic Gates Simulator is a Python application that models digital logic circuits. It uses an object-oriented approach where each gate is a class with inputs and output evaluation.

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Gate Classes                                │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌─────────────────────┐  │
│  │  AND   │ │   OR   │ │  NOT   │ │  Composite Gates    │  │
│  │ Gate   │ │  Gate  │ │  Gate  │ │ (NAND, NOR, XOR...) │  │
│  └────────┘ └────────┘ └────────┘ └─────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Circuit Builder                                 │
│              - Connect gates                                │
│              - Evaluate circuit                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Truth Table Generator                           │
└─────────────────────────────────────────────────────────────┘
```

## 3. File Structure

```
logic-gates-simulator/
├── gates.py           # Main gates implementation
├── specs/             # Documentation
└── README.md
```

---

*Document Version: 1.0*  
*Created: 2026-03-17*
