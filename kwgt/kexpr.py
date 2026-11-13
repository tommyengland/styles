"""Fully bracket Kustom formulas, so the result doesn't depend on KWGT's operator order.

KWGT appears to read `a != "" & b = 0` left to right, so every binary operation is wrapped in
brackets: (a != "") & (b = 0). Only the parts between $...$ are touched."""
import re

OPS = [["|"], ["&"], ["=", "!=", "<", ">", "<=", ">="], ["+", "-"], ["*", "/", "%"]]
TOKEN = re.compile(r'\s*(?:(?P<str>"[^"]*")|(?P<op><=|>=|!=|[=<>&|+\-*/%])|(?P<p>[(),])|(?P<atom>[^\s(),"=<>&|+\-*/%!]+))')


def tokens(s):
    out, pos = [], 0
    while pos < len(s):
        if s[pos:].strip() == "":
            break
        m = TOKEN.match(s, pos)
        if not m or m.end() == pos:
            raise ValueError(f"can't read formula at: {s[pos:pos + 30]!r}")
        kind = m.lastgroup
        out.append((kind, m.group(kind)))
        pos = m.end()
    return out


class P:
    def __init__(self, toks):
        self.t, self.i = toks, 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def take(self):
        tok = self.peek()
        self.i += 1
        return tok

    def expr(self, level=0):
        if level == len(OPS):
            return self.unary()
        left = self.expr(level + 1)
        while self.peek()[0] == "op" and self.peek()[1] in OPS[level]:
            op = self.take()[1]
            right = self.expr(level + 1)
            left = f"({left} {op} {right})"
        return left

    def unary(self):
        kind, val = self.peek()
        if kind == "op" and val == "-":
            self.take()
            return f"-{self.unary()}"
        if kind == "p" and val == "(":
            self.take()
            inner = self.expr()
            self.expect(")")
            return f"({inner})"
        if kind in ("str", "atom"):
            self.take()
            while kind == "atom" and self.peek()[0] == "atom":   # bare formats with spaces: df(d MMMM)
                val += " " + self.take()[1]
            if self.peek() == ("p", "("):          # a function call
                self.take()
                args = []
                if self.peek() != ("p", ")"):
                    args.append(self.expr())
                    while self.peek() == ("p", ","):
                        self.take()
                        args.append(self.expr())
                self.expect(")")
                return f"{val}({', '.join(args)})"
            return val
        raise ValueError(f"unexpected {val!r}")

    def expect(self, v):
        if self.take() != ("p", v):
            raise ValueError(f"expected {v!r}")


def bracket_expr(e):
    p = P(tokens(e))
    out = p.expr()
    if p.i != len(p.t):
        raise ValueError(f"left over in {e[:60]!r}")
    return out


def bracket(text):
    """Bracket every $...$ part of a Kustom string."""
    parts = text.split("$")
    if len(parts) < 3:
        return text
    for k in range(1, len(parts), 2):
        if parts[k].strip():
            parts[k] = bracket_expr(parts[k])
    return "$".join(parts)


FORMULA_KEYS = {"text_expression", "global_formula", "url", "switch_text"}


def bracket_tree(o, errors):
    if isinstance(o, dict):
        for k, v in list(o.items()):
            if isinstance(v, str) and (k in FORMULA_KEYS or "$" in v) and v.count("$") >= 2:
                try:
                    o[k] = bracket(v)
                except ValueError as e:
                    errors.append(f"{k}: {e}")
            else:
                bracket_tree(v, errors)
    elif isinstance(o, list):
        for x in o:
            bracket_tree(x, errors)
