from __future__ import annotations

from dataclasses import dataclass

from ifp_ast import (
    CHARS,
    CHARS_DECODED,
    TBinOp,
    TBool,
    TIf,
    TInt,
    TLam,
    TString,
    TUnOp,
    TVar,
    Term,
)


@dataclass(frozen=True)
class ParseError(Exception):
    kind: str
    index: int | None = None
    ch: str | None = None

    def __str__(self) -> str:
        if self.kind == "UnexpectedChar":
            return f"UnexpectedChar({self.ch!r}, {self.index})"
        if self.kind == "UnusedInput":
            return f"UnusedInput({self.index})"
        return "UnexpectedEOF"


# Helpers
def _decode_base94(body: str) -> int:
    val = 0
    for ch in body:
        # Base94: abc = a*94^2 + b*94 + c
        #             = (a*94 + b)*94 + c
        val = val * 94 + (ord(ch) - 33)
    return val


def _decode_string(body: str) -> str:
    decoded_chars = []
    for ch in body:
        char_index = ord(ch) - 33
        decoded_chars.append(CHARS_DECODED[char_index])
    return "".join(decoded_chars)


# Core func
def p_term(inp: str) -> Term:
    
    def get_tokens():
        tokens = inp.split(" ")
        index = 0
        for i, tok in enumerate(tokens):
            if i == len(tokens) - 1 and tok == "":
                break
            yield tok, index
            index += len(tok) + 1

    token_iterator = get_tokens()

    # Core recursion: read 1 token and return 1 AST node
    def parse_term() -> Term:
        try:
            token, index = next(token_iterator)
        except StopIteration:
            raise ParseError("UnexpectedEOF")

        if not token:
            raise ParseError("UnexpectedChar", index=index, ch=" ")

        for i_ch, char in enumerate(token):
            if not (33 <= ord(char) <= 126):
                raise ParseError("UnexpectedChar", index=index + i_ch, ch=char)

        indicator = token[0]
        body = token[1:]

        # Boolean Constants
        if indicator == "T":
            if body:
                raise ParseError("UnexpectedChar", index=index + 1, ch=body[0])
            return TBool(True)
        elif indicator == "F":
            if body:
                raise ParseError("UnexpectedChar", index=index + 1, ch=body[0])
            return TBool(False)

        # Integer Values
        elif indicator == "I":
            if not body:
                if index + 1 >= len(inp):
                    raise ParseError("UnexpectedEOF")
                else:
                    raise ParseError("UnexpectedChar", index=index + 1, ch=inp[index + 1])
            return TInt(_decode_base94(body))

        # String Values
        elif indicator == "S":
            return TString(_decode_string(body))

        # Unary Operators
        elif indicator == "U":
            if len(body) != 1:
                if not body:
                    if index + 1 >= len(inp): raise ParseError("UnexpectedEOF")
                    else: raise ParseError("UnexpectedChar", index=index + 1, ch=inp[index + 1])
                else:
                    raise ParseError("UnexpectedChar", index=index + 2, ch=body[1])
            operand = parse_term()
            return TUnOp(op=body, term=operand)

        # Binary Operators
        elif indicator == "B":
            if len(body) != 1:
                if not body:
                    if index + 1 >= len(inp): raise ParseError("UnexpectedEOF")
                    else: raise ParseError("UnexpectedChar", index=index + 1, ch=inp[index + 1])
                else:
                    raise ParseError("UnexpectedChar", index=index + 2, ch=body[1])
            left = parse_term()
            right = parse_term()
            return TBinOp(left=left, op=body, right=right)

        # Conditional Expression
        elif indicator == "?":
            if body:
                raise ParseError("UnexpectedChar", index=index + 1, ch=body[0])
            cond = parse_term()
            true_branch = parse_term()
            false_branch = parse_term()
            return TIf(cond=cond, true_branch=true_branch, false_branch=false_branch)

        # Variables
        elif indicator == "v":
            if not body:
                if index + 1 >= len(inp): raise ParseError("UnexpectedEOF")
                else: raise ParseError("UnexpectedChar", index=index + 1, ch=inp[index + 1])
            return TVar(_decode_base94(body))

        # Lambda Abstractions
        elif indicator == "L":
            if not body:
                if index + 1 >= len(inp): raise ParseError("UnexpectedEOF")
                else: raise ParseError("UnexpectedChar", index=index + 1, ch=inp[index + 1])
            var_id = _decode_base94(body)
            lam_body = parse_term()
            return TLam(var=var_id, body=lam_body)

        else:
            raise ParseError("UnexpectedChar", index=index, ch=indicator)

    # Start parsing
    root_term = parse_term()
    try:
        token, index = next(token_iterator)
        if not token:
            raise ParseError("UnexpectedChar", index=index, ch=" ")
        raise ParseError("UnusedInput", index=index)
    except StopIteration:
        pass

    return root_term
