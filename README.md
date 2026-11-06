# Interstellar Functional Program (IFP) Interpreter (CO2039 - Assignment 2)

A Python implementation of an Abstract Syntax Tree (AST) parser and runtime evaluator for the **Interstellar Functional Program (IFP)** language—a prefix-notation functional programming language featuring base-94 encoding, first-class functions, closures, and call-by-name evaluation. Developed as Assignment 2 for the **Advanced Programming (CO2039)** course at Ho Chi Minh City University of Technology (HCMUT - VNU-HCM), Semester 252.

## Overview

The IFP language models computation using an ICFP-inspired tokenized prefix syntax. The interpreter processes source expressions through a four-stage execution pipeline:

```text
Source Text ──> [ Parser ] ──> AST ──> [ Interpreter ] ──> Evaluated Value ──> [ Printer ] ──> Human & Encoded Output
```

### 1. Language Syntax & Encodings
- **Base-94 Integer Literals (`I...`)**: Non-empty character sequence interpreted as base-94 numbers (`!` represents 0, `"` represents 1, up to `~` representing 93).
- **Base-94 String Literals (`S...`)**: Encoded character sequences mapped via base-94 translation tables.
- **Boolean Constants**: `T` (`true`) and `F` (`false`).
- **Unary Operators (`U<op>`)**: Negation (`U-`), Logical NOT (`U!`).
- **Binary Operators (`B<op>`)**:
  - Arithmetic: `+`, `-`, `*`, `/`, `%`
  - Comparison: `<`, `>`, `=`
  - Logic: `|` (OR), `&` (AND)
  - String Operations: `.` (concatenation), `BT` (take $k$ chars), `BD` (drop $k$ chars)
  - Function Application: `B$ <function> <argument>`
- **Conditionals (`? <cond> <then> <else>`)**: Short-circuit branch evaluation.
- **First-Class Functions**:
  - Lambda abstraction: `L<var_id> <body>`
  - Variable reference: `v<var_id>`

### 2. Evaluation Engine (`interpreter.py`)
- **Lexical Closures (`VClosure`)**: Captures runtime environments at function creation time to preserve lexical scoping.
- **Call-by-Name & Lazy Evaluation (`Thunk`)**: Defers argument evaluation until required by primitive operations, supporting non-strict semantics and recursive definitions.
- **Safety Guards**: Enforces maximum beta-reduction limits (`MAX_STEPS`) to protect against infinite loops and non-terminating recursion.

## Project Structure

```text
.
├── src/
│   ├── ifp_ast.py                              # AST node class hierarchy
│   ├── parser.py                               # Recursive descent prefix parser
│   ├── interpreter.py                          # Core evaluator, closures & thunks
│   ├── printer.py                              # Pretty-printer & base-94 encoder
│   └── main.py                                 # Interactive CLI runner
├── tests/
│   └── test_interpreter.py                    # Comprehensive test suite (unittest)
├── specs/
│   └── AP_Ass2_Spec.pdf                        # Assignment specification
├── .gitignore                                  # Git ignore rules
├── LICENSE                                     # MIT License
├── README.md                                   # Project documentation
└── run.sh                                      # Execution and verification script
```

## Getting Started

### Prerequisites

- **Python** 3.8 or higher.

### Usage

1. **Interactive Mode**:
   ```bash
   python src/main.py
   ```
   Enter an encoded phrase (e.g., `B+ I" I#`) when prompted.

2. **Piped Input**:
   ```bash
   echo "B+ I\" I#" | python src/main.py
   ```

3. **Running the Test Suite**:
   ```bash
   python -m unittest discover tests
   ```
   Or execute the shell script:
   ```bash
   bash run.sh
   ```

## License

This project is licensed under the [MIT License](LICENSE).
