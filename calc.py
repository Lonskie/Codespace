import enum
from typing import List, Tuple, Set, Union

code = "91 + 6 * -(3 - -1)"

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

OPERATORS: Set[str] = { '+', '-', '*', '/', '^', '**' }
Token = Tuple[str, TokenType]
TokenStream = List[Token]

def char_type(char: str) -> TokenType:
    if char.isdigit():
        return TokenType.NUMBER
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
        current_type = char_type(char)
        
        if current_type is None:
            c += 1
            continue

        end_of_token = (c + 1 == end
            or char_type(string[c + 1]) is not current_type)

        if current_type in [TokenType.L_PAREN, TokenType.R_PAREN]:
            end_of_token = True

        acc.append(char)
        if end_of_token:
            tokens.append((''.join(acc), current_type))
            current_type = None
            acc = []
            
        c += 1
    

    return tokens

PRECEDENCE = {
    '+':  1, '-': 1,
    '*':  2, '/': 2,
    '**': 3, '^': 3,
}
precedence = lambda op: PRECEDENCE.get(op)

class Assoc(enum.Enum):
    LEFT    = 0
    RIGHT   = 1
    NEITHER = 2

ASSOC = {
    '+': Assoc.LEFT, '-': Assoc.LEFT,
    '*': Assoc.LEFT, '/': Assoc.LEFT,
    '**': Assoc.RIGHT, '^': Assoc.RIGHT,
}
assoc = lambda op: ASSOC.get(op) or Assoc.NEITHER

class BinOp(object):
    def __init__(self, root: str, left=None, right=None):
        self.value = root
        self.left:  Expr = left
        self.right: Expr = right
    def __str__(self):
        return f"({self.left} {self.value} {self.right})"

class UnOp(object):
    def __init__(self, root: str, operand=None):
        self.value: str = root
        self.operand: Expr = operand
    def __str__(self):
        return f"({self.value}{self.operand})"

Value = int
Expr = Union[UnOp, BinOp, Value]

def parse_prefix(tokens: TokenStream) -> Expr:
    value, token_type = tokens.pop(0)

    if token_type is TokenType.OPERATOR:
        return UnOp(value, parse_expr(tokens, precedence(value)))
    elif token_type is TokenType.NUMBER:
        return int(value)
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
        raise Exception(f"Expected an operator. Got '{value}'")
    prec = precedence(value)
    if prec is None:
        raise Exception(f"No such operator ('{value}') exists!")
    return prec

def parse_infix(left: Expr, tokens: TokenStream, prev_prec) -> Expr:
    token = tokens.pop(0)
    value, _ = token
    
    prec = token_precedence(token)
    if prev_prec == prec and assoc(value) is Assoc.RIGHT:
        prec -= 1

    return BinOp(value,
        left  = left,
        right = parse_expr(tokens, prec))

def parse_expr(tokens: TokenStream, prec=0) -> Expr:
    left = parse_prefix(tokens)
    if len(tokens) == 0:
        return left

    current_precedence = token_precedence(tokens[0])

    while prec < current_precedence:
        left = parse_infix(left, tokens, current_precedence)
        if len(tokens) == 0: break

        token = tokens[0]
        current_precedence = token_precedence(token)
        
    return left

OPERATIONS = {
    '+': lambda n, m: n + m,
    '-': lambda n, m=None: -n if m is None else n - m,
    '*': lambda n, m: n * m,
    '/': lambda n, m: n / m,
    '^': lambda n, m: n ** m,
    '**': lambda n, m: n ** m,
}
operation = lambda op: OPERATIONS.get(op)

def evaluate(expr: Expr) -> Value:
    expr_type = type(expr)
    if expr_type is Value:
        return expr

    function = operation(expr.value)
    if expr_type is BinOp:
        return function(
            evaluate(expr.left),
            evaluate(expr.right))
    if expr_type is UnOp:
        return function(evaluate(expr.operand))

print(code)
stream = tokenise(code)
#print(' '.join(map(lambda e: f'<{e[0]}>', stream)))
print(stream)
ast = parse_expr(stream)
print(ast)
result = evaluate(ast)
print(result)

def exec_string(code: str) -> Value:
    return evaluate(parse_expr(tokenise(code)))

print("\nNow you try!\n")

import readline
while True:
    prompt = "::> "
    line = input(prompt)
    if line.strip().lower().startswith("exit"):
        print("\nBuh-bye!")
        break
    try:
        expr = parse_expr(tokenise(line))
        print(f"\033[{len(line) + len(prompt)}C\033[1A = {expr}")
        print(f"#=> {evaluate(expr)}\n")
    except Exception as e:
        print(f"Error: {e}")