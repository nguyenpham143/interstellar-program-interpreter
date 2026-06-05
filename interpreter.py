from __future__ import annotations

from dataclasses import dataclass

from ifp_ast import TBinOp, TBool, TIf, TInt, TLam, TString, TUnOp, TVar, Term, CHARS_DECODED
from printer import encode_string, to_base94


MAX_STEPS = 10_000_000


class InterpreterError(Exception):
    pass


class BetaReductionLimit(InterpreterError):
    pass


class ScopeError(InterpreterError):
    pass


class TypeError_(InterpreterError):
    pass


class ArithmeticError_(InterpreterError):
    pass


class UnknownUnOp(InterpreterError):
    def __init__(self, op: str):
        super().__init__(f"Unknown unary operator: {op}")
        self.op = op


class UnknownBinOp(InterpreterError):
    def __init__(self, op: str):
        super().__init__(f"Unknown binary operator: {op}")
        self.op = op


@dataclass
class VInt:
    value: int


@dataclass
class VBool:
    value: bool


@dataclass
class VString:
    value: str


@dataclass
class VClosure:
    var: int
    body: Term
    env: dict[int, "Thunk"]


Value = VInt | VBool | VString | VClosure


@dataclass
class Thunk:
    kind: str
    value: Value | None = None
    steps: int = 0
    term: Term | None = None
    env: dict[int, "Thunk"] | None = None


def _to_term(v: Value) -> Term:
    if isinstance(v, VInt):
        return TInt(v.value)
    if isinstance(v, VBool):
        return TBool(v.value)
    if isinstance(v, VString):
        return TString(v.value)
    if isinstance(v, VClosure):
        return TLam(v.var, v.body)
    raise TypeError(f"Unknown value type: {type(v).__name__}")


def interpret(check_max: bool, term: Term) -> tuple[Term, int]:
    steps = 0
    
    def eval_term(t: Term, env: dict[int, Thunk]) -> Value:
        nonlocal steps

        if check_max and steps > MAX_STEPS:
            raise BetaReductionLimit()
        
        # TInt
        if isinstance(t, TInt):
            return VInt(t.value)
        
        # TBool
        elif isinstance(t, TBool):
            return VBool(t.value)
        
        # TString
        elif isinstance(t, TString):
            return VString(t.value)
        
        # TIf
        elif isinstance(t, TIf):
            cond_val = eval_term(t.cond, env)

            if not isinstance(cond_val, VBool):
                raise TypeError_()
            
            if cond_val.value is True:
                return eval_term(t.true_branch, env)
            else:
                return eval_term(t.false_branch, env)

        # TUnOp
        elif isinstance(t, TUnOp):
            operand_val = eval_term(t.term, env)
            
            if t.op == "-":
                if not isinstance(operand_val, VInt):
                    raise TypeError_()
                return VInt(-operand_val.value)

            elif t.op == "!":
                if not isinstance(operand_val, VBool):
                    raise TypeError_()
                return VBool(not operand_val.value)

            elif t.op == "#":
                if not isinstance(operand_val, VString):
                    raise TypeError_()
                
                encoded_str = encode_string(operand_val.value)
                val = 0
                for ch in encoded_str:
                    val = val * 94 + (ord(ch) - 33)

                return VInt(val)

            elif t.op == "$":
                if not isinstance(operand_val, VInt):
                    raise TypeError_()

                b94_str = to_base94(operand_val.value)
                if b94_str is None:
                    raise ArithmeticError_()

                decoded_chars = []
                for ch in b94_str:
                    char_index = ord(ch) - 33
                    decoded_chars.append(CHARS_DECODED[char_index])

                return VString("".join(decoded_chars))

            else:
                raise UnknownUnOp(t.op)

        # TBinOp
        elif isinstance(t, TBinOp):
            # Call-by-name
            if t.op == "$":
                steps += 1
                if check_max and steps > MAX_STEPS:
                    raise BetaReductionLimit()

                left_val = eval_term(t.left, env)
                if not isinstance(left_val, VClosure):
                    raise TypeError_()

                arg_thunk = Thunk(kind="lazy", term=t.right, env=env)
                
                new_env = left_val.env.copy()
                new_env[left_val.var] = arg_thunk

                return eval_term(left_val.body, new_env)

            # Strict evaluation
            else:
                left_val = eval_term(t.left, env)
                right_val = eval_term(t.right, env)
                
                if t.op == "+":
                    if not isinstance(left_val, VInt) or not isinstance(right_val, VInt):
                        raise TypeError_()
                    return VInt(left_val.value + right_val.value)

                elif t.op == "-":
                    if not isinstance(left_val, VInt) or not isinstance(right_val, VInt):
                        raise TypeError_()
                    return VInt(left_val.value - right_val.value)
                
                elif t.op == "*":
                    if not isinstance(left_val, VInt) or not isinstance(right_val, VInt):
                        raise TypeError_()
                    return VInt(left_val.value * right_val.value)

                elif t.op == "/":
                    if not isinstance(left_val, VInt) or not isinstance(right_val, VInt):
                        raise TypeError_()
                    if right_val.value == 0:
                        raise ArithmeticError_()
                    return VInt(int(left_val.value / right_val.value))

                elif t.op == "%":
                    if not isinstance(left_val, VInt) or not isinstance(right_val, VInt):
                        raise TypeError_()
                    if right_val.value == 0:
                        raise ArithmeticError_()

                    a = left_val.value
                    b = right_val.value
                    modulo = a - int(a / b) * b

                    return VInt(modulo)

                elif t.op == "<":
                    if not isinstance(left_val, VInt) or not isinstance(right_val, VInt):
                        raise TypeError_()
                    return VBool(left_val.value < right_val.value)

                elif t.op == ">":
                    if not isinstance(left_val, VInt) or not isinstance(right_val, VInt):
                        raise TypeError_()
                    return VBool(left_val.value > right_val.value)

                elif t.op == "=":
                    if type(left_val) != type(right_val):
                        raise TypeError_()
                    if isinstance(left_val, (VInt, VBool, VString)):
                        return VBool(left_val.value == right_val.value)
                    else:
                        raise TypeError_()

                elif t.op == "|":
                    if not isinstance(left_val, VBool) or not isinstance(right_val, VBool):
                        raise TypeError_()
                    return VBool(left_val.value or right_val.value)

                elif t.op == "&":
                    if not isinstance(left_val, VBool) or not isinstance(right_val, VBool):
                        raise TypeError_()
                    return VBool(left_val.value and right_val.value)

                elif t.op == ".":
                    if not isinstance(left_val, VString) or not isinstance(right_val, VString):
                        raise TypeError_()
                    return VString(left_val.value + right_val.value)

                elif t.op == "T":
                    if not isinstance(left_val, VInt) or not isinstance(right_val, VString):
                        raise TypeError_()
                    return VString(right_val.value[:left_val.value])

                elif t.op == "D":
                    if not isinstance(left_val, VInt) or not isinstance(right_val, VString):
                        raise TypeError_()
                    return VString(right_val.value[left_val.value:])

                else:
                    raise UnknownBinOp(t.op)

        # TVar
        elif isinstance(t, TVar):
            if t.value not in env:
                raise ScopeError()
            thunk = env[t.value]
            return eval_term(thunk.term, thunk.env)

        # TLam
        elif isinstance(t, TLam):
            return VClosure(var=t.var, body=t.body, env=env.copy())

        else:
            raise TypeError(f"Unknown term type: {type(t).__name__}")

    result = eval_term(term, {})
    return _to_term(result), steps
