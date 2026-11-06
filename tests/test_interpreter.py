import sys
import os
import unittest

# Ensure src directory is in the Python module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from ifp_ast import TBool, TInt, TString, Term
from parser import p_term, ParseError
from interpreter import (
    interpret,
    InterpreterError,
    BetaReductionLimit,
    ScopeError,
    TypeError_,
    ArithmeticError_,
)
from printer import pp_term


def eval_expr(program: str) -> Term:
    term = p_term(program)
    result, _ = interpret(check_max=False, term=term)
    return result


class TestIFPInterpreter(unittest.TestCase):

    def test_boolean_constants_and_logic(self):
        """Tests boolean literals and logical operators."""
        self.assertEqual(pp_term(eval_expr("T")), "T")
        self.assertEqual(pp_term(eval_expr("F")), "F")

        # Logical NOT (U!)
        self.assertEqual(pp_term(eval_expr("U! T")), "F")
        self.assertEqual(pp_term(eval_expr("U! F")), "T")

        # Logical AND (B&) and OR (B|)
        self.assertEqual(pp_term(eval_expr("B& T F")), "F")
        self.assertEqual(pp_term(eval_expr("B& T T")), "T")
        self.assertEqual(pp_term(eval_expr("B| T F")), "T")
        self.assertEqual(pp_term(eval_expr("B| F F")), "F")

    def test_integers_and_arithmetic(self):
        """Tests base-94 integer literals and arithmetic operations."""
        # ! = 0, " = 1, # = 2, $ = 3, % = 4, ' = 6
        res_0 = eval_expr("I!")
        self.assertIsInstance(res_0, TInt)
        self.assertEqual(res_0.value, 0)

        res_1 = eval_expr("I\"")
        self.assertEqual(res_1.value, 1)

        # Addition: 1 + 2 = 3
        res_add = eval_expr("B+ I\" I#")
        self.assertIsInstance(res_add, TInt)
        self.assertEqual(res_add.value, 3)

        # Subtraction: 3 - 1 = 2
        res_sub = eval_expr("B- I$ I\"")
        self.assertEqual(res_sub.value, 2)

        # Multiplication: 2 * 3 = 6
        res_mul = eval_expr("B* I# I$")
        self.assertEqual(res_mul.value, 6)

        # Integer Division: 7 / 2 = 3
        res_div = eval_expr("B/ I( I#")
        self.assertEqual(res_div.value, 3)

        # Modulo: 8 % 3 = 2
        res_mod = eval_expr("B% I) I$")
        self.assertEqual(res_mod.value, 2)

        # Unary Negation: -(1) = -1
        res_neg = eval_expr("U- I\"")
        self.assertEqual(res_neg.value, -1)

    def test_comparison_operators(self):
        """Tests binary comparison operators (<, >, =)."""
        self.assertEqual(pp_term(eval_expr("B< I\" I#")), "T")   # 1 < 2
        self.assertEqual(pp_term(eval_expr("B< I# I\"")), "F")   # 2 < 1
        self.assertEqual(pp_term(eval_expr("B> I# I\"")), "T")   # 2 > 1
        self.assertEqual(pp_term(eval_expr("B= I\" I\"")), "T")   # 1 == 1
        self.assertEqual(pp_term(eval_expr("B= I\" I#")), "F")   # 1 == 2

    def test_conditionals(self):
        """Tests conditional if-then-else expressions (?)."""
        # ? T 1 2 -> 1
        self.assertEqual(eval_expr("? T I\" I#").value, 1)
        # ? F 1 2 -> 2
        self.assertEqual(eval_expr("? F I\" I#").value, 2)
        # Short-circuiting with complex condition
        self.assertEqual(eval_expr("? B< I\" I# I$ I%").value, 3)

    def test_string_operations(self):
        """Tests string literals and string manipulation operations."""
        # String concatenation (B.)
        res_cat = eval_expr("B. S4% S34")
        self.assertIsInstance(res_cat, TString)

        # String Take (BT) and Drop (BD)
        res_take = eval_expr("BT I\" S4%34")
        self.assertIsInstance(res_take, TString)

        res_drop = eval_expr("BD I\" S4%34")
        self.assertIsInstance(res_drop, TString)

    def test_lambda_and_closures(self):
        """Tests first-class functions, application (B$), and closures."""
        # Identity function: (lambda v0. v0)(2) -> 2
        res_id = eval_expr("B$ L! v! I#")
        self.assertEqual(res_id.value, 2)

        # Increment: (lambda v0. v0 + 1)(2) -> 3
        res_inc = eval_expr("B$ L! B+ v! I\" I#")
        self.assertEqual(res_inc.value, 3)

        # Curried addition: ((lambda v1. lambda v0. v1 + v0)(2))(3) -> 5
        res_curried = eval_expr("B$ B$ L\" L! B+ v\" v! I# I$")
        self.assertEqual(res_curried.value, 5)

    def test_error_handling(self):
        """Tests runtime and parse error detection."""
        # Division by zero
        with self.assertRaises(ArithmeticError_):
            eval_expr("B/ I\" I!")

        # Unbound variable
        with self.assertRaises(ScopeError):
            eval_expr("v!")

        # Type mismatch (adding boolean to integer)
        with self.assertRaises(TypeError_):
            eval_expr("B+ T I\"")

        # Parse Error on malformed expression
        with self.assertRaises(ParseError):
            p_term("B+")


if __name__ == "__main__":
    unittest.main()
