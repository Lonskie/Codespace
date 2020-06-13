import enum
from typing import List, Tuple, Set, Union

examples = [
    "91 + 6 * -(3 - -1)",
    "2 - 3 - 4 + 4 ^ 3 ^ 2",
    "sin pi + 3",
    "sin 3!",
    "x = 9",
    "2(3x)",
    "cos(pi + x/3)",
    "3! / (4!(4-3)!)",
    "lambda = 512.16",
    "lambda_0 = 511.07",
    "c = 300_000_000",
    "c = 3E8",
    "3E8 (lambda - lambda_0)/lambda_0"
]

class TokenType(enum.Enum):
    NUMBER     = 0
    L_PAREN    = 1
    R_PAREN    = 2
    OPERATOR   = 3
    IDENTIFIER = 4

    def __str__(self):
        TT = self.__class__
        return {
            TT.NUMBER: "NUM",
            TT.L_PAREN: "LPAREN",
            TT.R_PAREN: "RPAREN",
            TT.OPERATOR: "OP",
            TT.IDENTIFIER: "IDENT",
        }.get(self)
    def __repr__(self):
        return self.__str__()

OPERATORS: Set[str] = { '+', '-', '*', '/', '^', '**', '!', '=', '%', '~', '>', '<', '<=', '>=' }
Token = Tuple[str, TokenType]
TokenStream = List[Token]

def char_type(char: str, old_type: TokenType) -> TokenType:
    if char.isdigit():
        if old_type is TokenType.IDENTIFIER:
            return TokenType.IDENTIFIER
        else:
            return TokenType.NUMBER
    elif (char == '.' or char == '_') and old_type in { TokenType.NUMBER, None }:
        return TokenType.NUMBER
    elif char == 'E' and old_type is TokenType.NUMBER:
        return TokenType.NUMBER
    elif char.isalpha() or char == '_':
        return TokenType.IDENTIFIER
    elif char in OPERATORS:
        return TokenType.OPERATOR
    elif char == '(':
        return TokenType.L_PAREN
    elif char == ')':
        return TokenType.R_PAREN
    else:
        return None

def tokenise(string: str) -> TokenStream:
    c, end = 0, len(string)
    current_type: TokenType = None
    acc: List[str] = []

    tokens: TokenStream = []
    while c < end:
        char = string[c]
        current_type = char_type(char, current_type)
        
        if current_type is None:
            c += 1
            continue

        end_of_token = (c + 1 == end
            or char_type(string[c + 1], current_type) is not current_type)

        if current_type in [TokenType.L_PAREN, TokenType.R_PAREN]:
            end_of_token = True

        acc.append(char)
        if end_of_token:
            tokens.append((''.join(acc), current_type))
            current_type = None
            acc = []
            
        c += 1
    

    return tokens

JUXTAPOSITION_PRECEDENCE = 9
PRECEDENCE = {
    '=': 1,
    '+':  3, '-': 3,
    '*':  4, '/': 4,
    '**': 5, '^': 5,
    '!': 10
}
precedence = lambda op: PRECEDENCE.get(op)

class Assoc(enum.Enum):
    LEFT    = 0
    RIGHT   = 1
    NEITHER = 2

ASSOC = {
    '=': Assoc.RIGHT,
    '+': Assoc.LEFT, '-': Assoc.LEFT,
    '*': Assoc.LEFT, '/': Assoc.LEFT,
    '**': Assoc.RIGHT, '^': Assoc.RIGHT,
}
assoc = lambda op: ASSOC.get(op) or Assoc.NEITHER

POSTFIX: Set['string'] = { '!' }
is_postfix = lambda op: op in POSTFIX

class BinOp(object):
    def __init__(self, root: str, left=None, right=None):
        self.value = root
        self.left:  Expr = left
        self.right: Expr = right
    def __str__(self):
        return f"({self.left} {self.value} {self.right})"

class UnOp(object):
    def __init__(self, root: str, operand=None, postfix=False):
        self.value: str = root
        self.operand: Expr = operand
        self.postfix = postfix
    def __str__(self):
        if self.postfix:
            return f"({self.operand}{self.value})"
        else:
            return f"({self.value}{self.operand})"

class Juxt(object):
    def __init__(self, callee, operand):
        self.callee: Expr = callee
        self.operand: Expr = operand
    def __str__(self):
        return f"({self.callee} {self.operand})"

class Symbol(object):
    def __init__(self, value):
        self.name = str(value)
    def __str__(self):
        return self.name

Number = Union[int, float]
Value = Union[Number, Symbol]
Expr = Union[UnOp, BinOp, Juxt, Value]

def parse_prefix(tokens: TokenStream) -> Expr:
    value, token_type = tokens.pop(0)

    if token_type is TokenType.OPERATOR:
        return UnOp(value, parse_expr(tokens, precedence(value)))
    elif token_type is TokenType.NUMBER:
        return float(value) if '.' in value or 'E' in value else int(value)
    elif token_type is TokenType.IDENTIFIER:
        return Symbol(value)
    elif token_type is TokenType.L_PAREN:
        expr = parse_expr(tokens, 0)
        if len(tokens) == 0 or tokens.pop(0)[1] is not TokenType.R_PAREN:
            raise Exception("Missing closing parenthesis.")
        return expr
    else:
        raise Exception(f"Expected something to the left.  Not expecting {value}.")

def token_precedence(token: Token) -> int:
    value, ttype = token
    if ttype is TokenType.R_PAREN:
        return 0
    if ttype is not TokenType.OPERATOR:
        # Juxtaposition is now allowd (function application)
        #raise Exception(f"Expected an operator. Got '{value}'")
        return JUXTAPOSITION_PRECEDENCE
    prec = precedence(value)
    if prec is None:
        raise Exception(f"No such operator ('{value}') exists!")
    return prec

def parse_infix(left: Expr, tokens: TokenStream, prev_prec) -> Expr:
    token = tokens.pop(0)
    value, ttype = token
    prec = None

    if ttype is TokenType.OPERATOR:
        prec = token_precedence(token)
    else:  # Juxtaposition / function-application.
        tokens.insert(0, token)
        return Juxt(left, parse_expr(tokens, JUXTAPOSITION_PRECEDENCE))  # High(est?) precende.

    if is_postfix(value):
        return UnOp(value, left, postfix=True)

    if assoc(value) is Assoc.RIGHT:
        prec -= 1
    elif assoc(value) is Assoc.NEITHER and prev_prec == prec:
        raise Exception("Cannot chain this operator with equal precedence."
            + " Please use parentheses.")

    return BinOp(value,
        left  = left,
        right = parse_expr(tokens, prec))

def parse_expr(tokens: TokenStream, prec=0) -> Expr:
    left = parse_prefix(tokens)
    if len(tokens) == 0:
        return left

    current_precedence = token_precedence(tokens[0])
    old_precedence = 0

    while prec < current_precedence:
        left = parse_infix(left, tokens, old_precedence)
        if len(tokens) == 0: break

        old_precedence = current_precedence
        current_precedence = token_precedence(tokens[0])
        
    return left

from functools import reduce
OPERATIONS = {
    '+': lambda n, m: n + m,
    '-': lambda n, m=None: -n if m is None else n - m,
    '*': lambda n, m: n * m,
    '/': lambda n, m: n / m,
    '^': lambda n, m: n ** m,
    '**': lambda n, m: n ** m,
    '!': lambda n: reduce(lambda acc, e: acc * e, range(2, n+1), 1),
    '=': lambda ctx, sym, val: ctx.define(sym, val)
}
operation = lambda op: OPERATIONS.get(op)

class Context(object):
    def __init__(self, initial=None):
        self.symbols = initial or dict()
    def define(self, sym: str, value: Value):
        self.symbols[sym] = value
        return value
    def lookup(self, sym: str):
        if sym in self.symbols:
            return self.symbols[sym]
        raise Exception(f"Variable `{sym}', not defined.")

def evaluate(expr: Expr, ctx: Context) -> Value:
    expr_type = type(expr)
    if expr_type is Symbol:
        return ctx.lookup(expr.name)
    if expr_type in Value.__args__:
        return expr

    if expr_type is Juxt:
        callee = evaluate(expr.callee, ctx)
        operand = evaluate(expr.operand, ctx)
        if type(callee) in Number.__args__: # Juxtaposition of numbers is multiplication.
            return callee * operand
        elif not callable(callee):
            raise Exception(f"Juxtaposition is not defined on `{callee}'.")
        return callee(operand)

    function = operation(expr.value)
    if expr_type is BinOp:
        if expr.value == '=':
            if type(expr.left) is Symbol:
                return function(ctx,
                    expr.left.name,
                    evaluate(expr.right, ctx))
            else:
                raise Exception("Can only assign to symbols.")
        return function(
            evaluate(expr.left, ctx),
            evaluate(expr.right, ctx))
    if expr_type is UnOp:
        return function(evaluate(expr.operand, ctx))

import math
base_context = Context({
    'sqrt': math.sqrt,
    'sin': math.sin,
    'cos': math.cos,
    'pi': math.pi,
})

for (i, code) in enumerate(examples):
    print(f"\nExample {i + 1}:")
    tab = "   "
    print(tab, code)
    stream = tokenise(code)
    print(tab, ' '.join(map(lambda e: f'<{e[0]}>', stream)))
    #print(tab, stream)
    ast = parse_expr(stream)
    print(tab, ast)
    result = evaluate(ast, base_context)
    print(tab, result)

def exec_string(code: str, ctx: Context) -> Value:
    return evaluate(parse_expr(tokenise(code)), ctx)

print("\nNow you try!\n")

import readline
while True:
    prompt = "::> "
    line = input(prompt)
    trimmed = line.strip().lower()
    if trimmed.startswith("exit"):
        print("\nBuh-bye!")
        break
    if len(trimmed) == 0:
        continue
    try:
        expr = parse_expr(tokenise(line))
        print(f"\033[{len(line) + len(prompt)}C\033[1A ≡ {expr}")
        print(f"#=> {evaluate(expr, base_context)}\n")
    except Exception as e:
        print(f"Error: {e}")