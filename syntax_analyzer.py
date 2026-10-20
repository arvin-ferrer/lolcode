from model.lexeme import Lexeme
from model.token import Token
from model.node import Node

class Parser():
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens    # List of tokens
        self.pos = 0            # Current position of the token that is parsed

    def current_token(self) -> Token | None:
        """
        Returns the current token or None if at the end of the token list.
        """
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume_tokens(
            self, 
            expected: Token|None = None, 
            convert:  Token|None = None
        ) -> Node:
        """
        Consumes the current token and returns a Node containing it.
        If 'expected' is provided, checks if the current token matches it.
        If 'convert' is provided, changes the token type to 'convert' before returning.
        """
        token = self.current_token()
        if not token:
            raise SyntaxError("Unexpected end of input encountered.")
        if expected and token.type != expected:
            raise SyntaxError(f"Expected {expected}, got {token.type} ({token.lexeme})")
        if convert:
            token.type = convert
        self.pos += 1
        return Node(token)

    def parse(self) -> Node:
        """
        Starts the parsing process and returns the root of the parse tree.
        """
        tree = self.program()
        if self.pos < len(self.tokens):
            raise SyntaxError("Unexpected characters at end of input {}".format(self.tokens[self.pos:]))
        return tree
    
    # <program> ::= <outer_blocks> HAI <linebreak> <variables_dec> <statement_list> KTHXBYE <outer_blocks>
    def program(self) -> Node:
        node = Node("program")
        node.children.append(self.outer_blocks())
        node.children.append(self.consume_tokens(expected=Lexeme.HAI))  # HAI
        node.children.append(self.linebreak())
        node.children.append(self.variables_dec())
        node.children.append(self.statement_list())
        node.children.append(self.consume_tokens(expected=Lexeme.KTHXBYE))  # KTHXBYE
        node.children.append(self.outer_blocks())
        return node

    # <outer_blocks> ::= <func_def> <linebreak> <outer_blocks> | <comments> <outer_blocks> | <linebreak> | ε 
    def outer_blocks(self) -> Node:
        node = Node("outer_blocks")
        if self.current_token() and self.current_token().type == Lexeme.HOW_IZ_I:
            node.children.append(self.func_def())
            node.children.append(self.linebreak())
            node.children.append(self.outer_blocks())
        elif self.current_token() and self.current_token().type in [Lexeme.BTW, Lexeme.OBTW]:
            node.children.append(self.comments())
            node.children.append(self.outer_blocks())
        elif self.current_token() and self.current_token().type == Lexeme.NEWLINE:
            node.children.append(self.linebreak()) 
        else:
            pass # Epsilon
        return node
    
    # <statement_list> ::= <statement> <linebreak> <statement_list> | <linebreak> <statement_list> | ε
    def statement_list(self) -> Node:
        node = Node("statement_list")
        
        statement_starters = [
            Lexeme.VISIBLE, Lexeme.I_HAS_A, Lexeme.GIMMEH,
            Lexeme.O_RLY, Lexeme.WTF, Lexeme.IM_IN_YR, Lexeme.HOW_IZ_I,
            Lexeme.FOUND_YR, Lexeme.I_IZ, Lexeme.MKAY,
            Lexeme.BTW, Lexeme.OBTW, Lexeme.GTFO,
            Lexeme.NUMBR_LITERAL, Lexeme.NUMBAR_LITERAL, Lexeme.YARN_LITERAL, Lexeme.TROOF_LITERAL, Lexeme.NOOB_LITERAL,
            Lexeme.SUM_OF, Lexeme.DIFF_OF, Lexeme.PRODUKT_OF, Lexeme.QUOSHUNT_OF,
            Lexeme.MOD_OF, Lexeme.BIGGR_OF, Lexeme.SMALLR_OF, Lexeme.BOTH_OF,
            Lexeme.EITHER_OF, Lexeme.WON_OF, Lexeme.NOT, Lexeme.ANY_OF, Lexeme.ALL_OF,
            Lexeme.BOTH_SAEM, Lexeme.DIFFRINT, Lexeme.SMOOSH, Lexeme.MAEK
        ]
        
        if self.current_token() and self.current_token().type in statement_starters:
            node.children.append(self.statement())
            node.children.append(self.linebreak())
            node.children.append(self.statement_list())
        elif self.current_token() and self.current_token().type == Lexeme.NEWLINE:
            node.children.append(self.consume_tokens(expected=Lexeme.NEWLINE))  # newline
            node.children.append(self.statement_list())
        else:
            pass # Epsilon
        return node

    # <statement> ::= <print> | <declaration> | <assignment> | <input> | <conditional> | <switch> | <loop> | <func_def> | <return_stmt> | <typecast_stmt> | <inline_comment> | <multi_comment> | <expression> | GTFO
    def statement(self) -> Node:
        node = Node("statement")
        if self.current_token() and self.current_token().type == Lexeme.VISIBLE:
            node.children.append(self.print())
        elif self.current_token() and self.current_token().type == Lexeme.I_HAS_A:
            node.children.append(self.declaration())
        elif self.current_token() and self.current_token().type == Lexeme.IDENTIFIER:
            if self.pos + 1 < len(self.tokens):
                next_type = self.tokens[self.pos + 1].type
                if next_type == Lexeme.R:
                    node.children.append(self.assignment())
                elif next_type == getattr(Lexeme, 'IS_NOW_A', None): # Assuming IS_NOW_A lexeme exists
                    node.children.append(self.typecast_stmt())
                else:
                    node.children.append(self.expression())
            else:
                node.children.append(self.expression())
        elif self.current_token() and self.current_token().type == Lexeme.GIMMEH:
            node.children.append(self.input())
        elif self.current_token() and self.current_token().type == Lexeme.O_RLY:
            node.children.append(self.conditional())
        elif self.current_token() and self.current_token().type == Lexeme.WTF:
            node.children.append(self.switch())
        elif self.current_token() and self.current_token().type == Lexeme.IM_IN_YR:
            node.children.append(self.loop())
        elif self.current_token() and self.current_token().type == Lexeme.HOW_IZ_I:
            node.children.append(self.func_def())
        elif self.current_token() and self.current_token().type == Lexeme.FOUND_YR:
            node.children.append(self.return_stmt())
        elif self.current_token() and self.current_token().type == Lexeme.MKAY:
            node.children.append(self.consume_tokens(expected=Lexeme.MKAY))  # MKAY
        elif self.current_token() and self.current_token().type == Lexeme.BTW:
            node.children.append(self.inline_comment())
        elif self.current_token() and self.current_token().type == Lexeme.OBTW:
            node.children.append(self.multi_comment())
        elif self.current_token() and self.current_token().type == Lexeme.GTFO:
            node.children.append(self.consume_tokens(expected=Lexeme.GTFO))  # GTFO
        else:
            # Fallback to expression for math operations acting as standalone statements
            node.children.append(self.expression())
        return node

    # <print> ::= VISIBLE <print_list>
    def print(self) -> Node:
        node = Node("print")
        node.children.append(self.consume_tokens(expected=Lexeme.VISIBLE))  # VISIBLE
        node.children.append(self.print_list())
        return node
    
    # <print_list> ::= <expression> | <expression> + <print_list>
    def print_list(self) -> Node:
        node = Node("print_list")
        node.children.append(self.expression())
        if self.current_token() and self.current_token().type == Lexeme.PLUS:
            node.children.append(self.consume_tokens(expected=Lexeme.PLUS))  # +
            node.children.append(self.print_list())
        return node
    
    # <literal> ::= numbr_NUMBR_LITERAL | numbar_NUMBAR_LITERAL | yarn_YARN_LITERAL | troof_TROOF_LITERAL
    def literal(self) -> Node:
        node = Node("literal")
        if self.current_token() and self.current_token().type in [Lexeme.NUMBR_LITERAL, Lexeme.NUMBAR_LITERAL, Lexeme.YARN_LITERAL, Lexeme.TROOF_LITERAL]:
            node.children.append(self.consume_tokens(expected=self.current_token().type))
        else:
            raise SyntaxError("Expected a literal")
        return node

    # <type> ::= YARN_LITERAL | NUMBR_LITERAL | NUMBAR_LITERAL | TROOF_LITERAL | NOOB_LITERAL
    def type(self) -> Node:
        node = Node("type")
        if self.current_token() and self.current_token().type == Lexeme.TYPE_LITERAL:
            node.children.append(self.consume_tokens(expected=self.current_token().type))
        else:
            raise SyntaxError(f"Expected a type token, got {self.current_token()}")
        return node
    
    # <variables_dec> ::= WAZZUP <linebreak> <vars> BUHBYE <linebreak> | ε
    def variables_dec(self) -> Node:
        node = Node("variables_dec")
        if self.current_token() and self.current_token().type == Lexeme.WAZZUP:
            node.children.append(self.consume_tokens(expected=Lexeme.WAZZUP))  # WAZZUP
            node.children.append(self.linebreak())
            node.children.append(self.vars())
            node.children.append(self.consume_tokens(expected=Lexeme.BUHBYE))  # BUHBYE
            node.children.append(self.linebreak())
        else:
            pass # Epsilon
        return node
    
    # <vars> ::= <declaration> <linebreak> <vars> | <linebreak> <vars> | <multi_comment> <linebreak> <vars> | ε
    def vars(self) -> Node:
        node = Node("vars")
        if self.current_token() and self.current_token().type == Lexeme.I_HAS_A:
            node.children.append(self.declaration())
            node.children.append(self.linebreak())
            node.children.append(self.vars())
        elif self.current_token() and self.current_token().type == Lexeme.NEWLINE:
            node.children.append(self.consume_tokens(expected=Lexeme.NEWLINE))  # newline
            node.children.append(self.vars())
        elif self.current_token() and self.current_token().type == Lexeme.OBTW:
            node.children.append(self.multi_comment())
            node.children.append(self.linebreak())
            node.children.append(self.vars())
        else:
            pass # Epsilon
        return node
    
    # <declaration> ::= I HAS A varident | I HAS A varident ITZ <expression>
    def declaration(self) -> Node:
        node = Node("declaration")
        node.children.append(self.consume_tokens(expected=Lexeme.I_HAS_A))  # I HAS A
        node.children.append(self.consume_tokens(expected=Lexeme.IDENTIFIER, convert=Lexeme.VARIABLE_IDENTIFIER))  # VARIABLE_IDENTIFIER
        if self.current_token() and self.current_token().type == Lexeme.ITZ:
            node.children.append(self.consume_tokens(expected=Lexeme.ITZ))  # ITZ
            node.children.append(self.expression())
        return node
    
    # <assignment> ::= varident R <expression>
    def assignment(self) -> Node:
        node = Node("assignment")
        node.children.append(self.consume_tokens(expected=Lexeme.IDENTIFIER, convert=Lexeme.VARIABLE_IDENTIFIER))  # VARIABLE_IDENTIFIER
        node.children.append(self.consume_tokens(expected=Lexeme.R))  # R
        node.children.append(self.expression())
        return node
    
    # <input> ::= GIMMEH varident
    def input(self) -> Node:
        node = Node("input")
        node.children.append(self.consume_tokens(expected=Lexeme.GIMMEH))  # GIMMEH
        node.children.append(self.consume_tokens(expected=Lexeme.IDENTIFIER, convert=Lexeme.VARIABLE_IDENTIFIER))  # VARIABLE_IDENTIFIER
        return node
    
    # <expression> ::= <operand> | <arithmetic_expr> | <boolean_expr> | <comparison_expr> | <concatenation_expr> | <typecast_expr> | <func_call>
    def expression(self) -> Node:
        node = Node("expression")
        if self.current_token() and self.current_token().type in [Lexeme.IDENTIFIER, Lexeme.NUMBR_LITERAL, Lexeme.NUMBAR_LITERAL, Lexeme.YARN_LITERAL, Lexeme.TROOF_LITERAL]:
            node.children.append(self.operand())
        elif self.current_token() and self.current_token().type in [Lexeme.SUM_OF, Lexeme.DIFF_OF, Lexeme.PRODUKT_OF, Lexeme.QUOSHUNT_OF, Lexeme.MOD_OF, Lexeme.BIGGR_OF, Lexeme.SMALLR_OF]:
            node.children.append(self.arithmetic_expr())
        elif self.current_token() and self.current_token().type in [Lexeme.BOTH_OF, Lexeme.EITHER_OF, Lexeme.WON_OF, Lexeme.NOT, Lexeme.ANY_OF, Lexeme.ALL_OF]:
            node.children.append(self.boolean_expr())
        elif self.current_token() and self.current_token().type in [Lexeme.BOTH_SAEM, Lexeme.DIFFRINT]:
            node.children.append(self.comparison_expr())
        elif self.current_token() and self.current_token().type == Lexeme.SMOOSH:
            node.children.append(self.concatenation_expr())
        elif self.current_token() and self.current_token().type == Lexeme.MAEK:
            node.children.append(self.typecast_expr())
        elif self.current_token() and self.current_token().type == Lexeme.I_IZ:
            node.children.append(self.func_call())
        else:
            raise SyntaxError(f"Unexpected token in expression: {self.current_token()}")
        return node
    
    # <operand> ::= varident | <literal>
    def operand(self) -> Node:
        node = Node("operand")
        if self.current_token() and self.current_token().type == Lexeme.IDENTIFIER:
            node.children.append(self.consume_tokens(expected=Lexeme.IDENTIFIER, convert=Lexeme.VARIABLE_IDENTIFIER))  # VARIABLE_IDENTIFIER
        else:
            node.children.append(self.literal())
        return node
    
    # <arithmetic_expr> ::= SUM OF <expression> AN <expression> | DIFF OF <expression> AN <expression> | PRODUKT OF <expression> AN <expression> | QUOSHUNT OF <expression> AN <expression> | MOD OF <expression> AN <expression> | BIGGR OF <expression> AN <expression> | SMALLR OF <expression> AN <expression>
    def arithmetic_expr(self) -> Node:
        node = Node("arithmetic_expr")
        if self.current_token() and self.current_token().type in [
            Lexeme.SUM_OF, Lexeme.DIFF_OF, Lexeme.PRODUKT_OF,
            Lexeme.QUOSHUNT_OF, Lexeme.MOD_OF, Lexeme.BIGGR_OF,
            Lexeme.SMALLR_OF
        ]:
            node.children.append(self.consume_tokens(expected=self.current_token().type))  # Operation
            node.children.append(self.expression())
            node.children.append(self.consume_tokens(expected=Lexeme.AN))  # AN
            node.children.append(self.expression())
        else:
            raise SyntaxError("Unexpected token in arithmetic expression")
        return node
    
    # <boolean_expr> ::= BOTH OF <expression> AN <expression> | ...
    def boolean_expr(self) -> Node:
        node = Node("boolean_expr")
        if self.current_token() and self.current_token().type in [
            Lexeme.BOTH_OF, Lexeme.EITHER_OF, Lexeme.WON_OF
        ]:
            node.children.append(self.consume_tokens(expected=self.current_token().type))  # Operation
            node.children.append(self.expression())
            node.children.append(self.consume_tokens(expected=Lexeme.AN))  # AN
            node.children.append(self.expression())
        elif self.current_token() and self.current_token().type == Lexeme.NOT:
            node.children.append(self.consume_tokens(expected=Lexeme.NOT))  # NOT
            node.children.append(self.expression())
        elif self.current_token() and self.current_token().type in [Lexeme.ANY_OF, Lexeme.ALL_OF]:
            node.children.append(self.consume_tokens(expected=self.current_token().type))  # ANY OF, ALL OF
            node.children.append(self.expr_list())
            node.children.append(self.consume_tokens(expected=Lexeme.MKAY))  # MKAY
        else:
            raise SyntaxError("Unexpected token in boolean expression")
        return node
    
    # <expr_list> ::= <expression> | <expression> AN <expr_list>
    def expr_list(self) -> Node:
        node = Node("expr_list")
        node.children.append(self.expression())
        if self.current_token() and self.current_token().type == Lexeme.AN:
            node.children.append(self.consume_tokens(expected=Lexeme.AN))  # AN
            node.children.append(self.expr_list())
        return node
    
    # <comparison_expr> ::= BOTH SAEM <expression> AN <expression> | DIFFRINT <expression> AN <expression>
    def comparison_expr(self) -> Node:
        node = Node("comparison_expr")
        if self.current_token() and self.current_token().type in [Lexeme.BOTH_SAEM, Lexeme.DIFFRINT]:
            node.children.append(self.consume_tokens(expected=self.current_token().type))  # BOTH SAEM or DIFFRINT
            node.children.append(self.expression())
            node.children.append(self.consume_tokens(expected=Lexeme.AN))  # AN
            node.children.append(self.expression())
        else:
            raise SyntaxError("Unexpected token in comparison expression")
        return node
    
    # <concatenation_expr> ::= SMOOSH <expr_list> | SMOOSH <expr_list> MKAY
    def concatenation_expr(self) -> Node:
        node = Node("concatenation_expr")
        node.children.append(self.consume_tokens(expected=Lexeme.SMOOSH))  # SMOOSH
        node.children.append(self.expr_list())
        if self.current_token() and self.current_token().type == Lexeme.MKAY:
            node.children.append(self.consume_tokens(expected=Lexeme.MKAY))  # MKAY
        return node
    
    # <typecast_expr> ::= MAEK <expression> A type | MAEK <expression> type
    def typecast_expr(self) -> Node:
        node = Node("typecast_expr")
        node.children.append(self.consume_tokens(expected=Lexeme.MAEK))  # MAEK
        node.children.append(self.expression())
        if self.current_token() and self.current_token().type == Lexeme.A:
            node.children.append(self.consume_tokens(expected=Lexeme.A))  # A
        node.children.append(self.type())
        return node
    
    # <typecast_stmt> ::= varident IS NOW A type
    def typecast_stmt(self) -> Node:
        node = Node("typecast_stmt")
        node.children.append(self.consume_tokens(expected=Lexeme.IDENTIFIER, convert=Lexeme.VARIABLE_IDENTIFIER))  # VARIABLE_IDENTIFIER
        node.children.append(self.consume_tokens(expected=Lexeme.IS_NOW_A))  # IS NOW A (Assuming your lexer bundles this into 1 token)
        node.children.append(self.type())
        return node
    
    # <conditional> ::= O RLY? <linebreak> YA RLY <linebreak> <statement_list> <mebbe_blocks> <no_wai_block> OIC
    def conditional(self) -> Node:
        node = Node("conditional")
        node.children.append(self.consume_tokens(expected=Lexeme.O_RLY))  # O RLY
        node.children.append(self.linebreak())
        node.children.append(self.consume_tokens(expected=Lexeme.YA_RLY))  # YA RLY
        node.children.append(self.linebreak())
        node.children.append(self.statement_list())
        node.children.append(self.mebbe_blocks())
        node.children.append(self.no_wai_block())
        node.children.append(self.consume_tokens(expected=Lexeme.OIC))  # OIC
        return node

    # <mebbe_blocks> ::= MEBBE <expression> <linebreak> <statement_list> <mebbe_blocks> | ε
    def mebbe_blocks(self) -> Node:
        node = Node("mebbe_blocks")
        if self.current_token() and self.current_token().type == Lexeme.MEBBE:
            node.children.append(self.consume_tokens(expected=Lexeme.MEBBE))
            node.children.append(self.expression())
            node.children.append(self.linebreak())
            node.children.append(self.statement_list())
            node.children.append(self.mebbe_blocks())
        return node

    # <no_wai_block> ::= NO WAI <linebreak> <statement_list> | ε
    def no_wai_block(self) -> Node:
        node = Node("no_wai_block")
        if self.current_token() and self.current_token().type == Lexeme.NO_WAI:
            node.children.append(self.consume_tokens(expected=Lexeme.NO_WAI))
            node.children.append(self.linebreak())
            node.children.append(self.statement_list())
        return node

    # <switch> ::= WTF? <linebreak> <case_blocks> <default_block> OIC
    def switch(self) -> Node:
        node = Node("switch")
        node.children.append(self.consume_tokens(expected=Lexeme.WTF))
        node.children.append(self.linebreak())
        node.children.append(self.case_blocks())
        node.children.append(self.default_block())
        node.children.append(self.consume_tokens(expected=Lexeme.OIC))  # OIC
        return node

    # <case_blocks> ::= OMG <literal> <linebreak> <statement_list> | OMG <literal> <linebreak> <statement_list> <case_blocks>
    def case_blocks(self) -> Node:
        node = Node("case_blocks")
        if self.current_token() and self.current_token().type == Lexeme.OMG:
            node.children.append(self.consume_tokens(expected=Lexeme.OMG))
            node.children.append(self.literal())
            node.children.append(self.linebreak())
            node.children.append(self.statement_list())
            node.children.append(self.case_blocks())
        return node

    # <default_block> ::= OMGWTF <linebreak> <statement_list> | ε
    def default_block(self) -> Node:
        node = Node("default_block")
        if self.current_token() and self.current_token().type == Lexeme.OMGWTF:
            node.children.append(self.consume_tokens(expected=Lexeme.OMGWTF))
            node.children.append(self.linebreak())
            node.children.append(self.statement_list())
        return node

    # <loop> ::= IM IN YR loopident <loop_action> YR varident <loop_cond> <linebreak> <statement_list> <linebreak> IM OUTTA YR loopident
    def loop(self) -> Node:
        node = Node("loop")
        node.children.append(self.consume_tokens(expected=Lexeme.IM_IN_YR))  # IM IN YR
        node.children.append(self.consume_tokens(expected=Lexeme.IDENTIFIER, convert=Lexeme.LOOP_IDENTIFIER)) 
        node.children.append(self.loop_action())
        node.children.append(self.consume_tokens(expected=Lexeme.YR))  # YR
        node.children.append(self.consume_tokens(expected=Lexeme.IDENTIFIER, convert=Lexeme.VARIABLE_IDENTIFIER))  # VARIABLE_IDENTIFIER
        node.children.append(self.loop_cond())
        node.children.append(self.linebreak())
        node.children.append(self.statement_list())
        node.children.append(self.linebreak())
        node.children.append(self.consume_tokens(expected=Lexeme.IM_OUTTA_YR))  # IM OUTTA YR
        node.children.append(self.consume_tokens(expected=Lexeme.IDENTIFIER, convert=Lexeme.LOOP_IDENTIFIER))  
        return node

    # <loop_action> ::= UPPIN | NERFIN
    def loop_action(self) -> Node:
        node = Node("loop_action")
        if self.current_token() and self.current_token().type in [Lexeme.UPPIN, Lexeme.NERFIN]:
            node.children.append(self.consume_tokens(expected=self.current_token().type))
        else:
            raise SyntaxError("Expected loop action")
        return node

    # <loop_cond> ::= TIL <expression> | WILE <expression> | ε
    def loop_cond(self) -> Node:
        node = Node("loop_cond")
        if self.current_token() and self.current_token().type in [Lexeme.TIL, Lexeme.WILE]:
            node.children.append(self.consume_tokens(expected=self.current_token().type))
            node.children.append(self.expression())
        return node

    # <func_def> ::= HOW IZ I funcident <linebreak> <statement_list> IF U SAY SO | HOW IZ I funcident <func_params> <linebreak> <statement_list> IF U SAY SO
    def func_def(self) -> Node:
        node = Node("func_def")
        node.children.append(self.consume_tokens(expected=Lexeme.HOW_IZ_I))
        node.children.append(self.consume_tokens(expected=Lexeme.IDENTIFIER, convert=Lexeme.FUNCTION_IDENTIFIER))  # VARIABLE_IDENTIFIER
        if self.current_token() and self.current_token().type == Lexeme.YR:
            node.children.append(self.func_params())
        node.children.append(self.linebreak())
        node.children.append(self.statement_list())
        node.children.append(self.consume_tokens(expected=Lexeme.IF_U_SAY_SO))  # IF U SAY SO
        return node

    # <func_params> ::= YR varident | YR varident AN <func_params>
    def func_params(self) -> Node:
        node = Node("func_params")
        node.children.append(self.consume_tokens(expected=Lexeme.YR))  # YR
        node.children.append(self.consume_tokens(expected=Lexeme.IDENTIFIER, convert=Lexeme.VARIABLE_IDENTIFIER))  # VARIABLE_IDENTIFIER
        if self.current_token() and self.current_token().type == Lexeme.AN:
            node.children.append(self.consume_tokens(expected=Lexeme.AN))  # AN
            node.children.append(self.func_params())
        return node

    # <return_stmt> ::= FOUND YR <expression>
    def return_stmt(self) -> Node:
        node = Node("return_stmt")
        node.children.append(self.consume_tokens(expected=Lexeme.FOUND_YR))
        node.children.append(self.expression())
        return node

    # <func_call> ::= I IZ funcident MKAY | I IZ funcident <call_args> MKAY
    def func_call(self) -> Node:
        node = Node("func_call")
        node.children.append(self.consume_tokens(expected=Lexeme.I_IZ))
        node.children.append(self.consume_tokens(expected=Lexeme.IDENTIFIER, convert=Lexeme.FUNCTION_IDENTIFIER)) 
        if self.current_token() and self.current_token().type == Lexeme.YR:
            node.children.append(self.call_args())
        node.children.append(self.consume_tokens(expected=Lexeme.MKAY))  # MKAY
        return node

    # <call_args> ::= YR <expression> | YR <expression> AN <call_args>
    def call_args(self) -> Node:
        node = Node("call_args")
        node.children.append(self.consume_tokens(expected=Lexeme.YR))  # YR
        node.children.append(self.expression())
        if self.current_token() and self.current_token().type == Lexeme.AN:
            node.children.append(self.consume_tokens(expected=Lexeme.AN))
            node.children.append(self.call_args())
        return node

    # <linebreak> ::= <newline> | <inline_comment> <newline> | ε
    def linebreak(self) -> Node:
        node = Node("linebreak")
        if self.current_token() and self.current_token().type == Lexeme.BTW:
            node.children.append(self.inline_comment())
        if self.current_token() and self.current_token().type == Lexeme.NEWLINE:
            # Consume all \n newlines
            while self.current_token() and self.current_token().type == Lexeme.NEWLINE:
                node.children.append(self.consume_tokens(expected=Lexeme.NEWLINE))
        else:
            pass
        return node

    # <comments> ::= <linebreak> <comments> | <multi_comment> <linebreak> <comments> | ε
    def comments(self) -> Node:
        node = Node("comments")
        if self.current_token() and self.current_token().type == Lexeme.OBTW:
            node.children.append(self.multi_comment())
            node.children.append(self.linebreak())
            node.children.append(self.comments())
        elif self.current_token() and self.current_token().type in [Lexeme.BTW, Lexeme.NEWLINE]:
            node.children.append(self.linebreak())
            node.children.append(self.comments())
        return node

    # <inline_comment> ::= BTW <comment> | BTW
    def inline_comment(self) -> Node:
        node = Node("inline_comment")
        node.children.append(self.consume_tokens(expected=Lexeme.BTW)) # BTW
        while self.current_token() and self.current_token().type == Lexeme.COMMENT_IDENTIFIER:
            node.children.append(self.comment())
        return node

    # <multi_comment> ::= OBTW newline <comment_body> TLDR
    def multi_comment(self) -> Node:
        node = Node("multi_comment")
        node.children.append(self.consume_tokens(expected=Lexeme.OBTW))
        node.children.append(self.consume_tokens(expected=Lexeme.NEWLINE))  # newline
        node.children.append(self.comment_body())
        node.children.append(self.consume_tokens(expected=Lexeme.TLDR))  # TLDR
        return node

    # <comment_body> ::= <comment> <newline> <comment_body> | <newline> <comment_body> | ε
    def comment_body(self) -> Node:
        node = Node("comment_body")
        if self.current_token() and self.current_token().type == Lexeme.COMMENT_IDENTIFIER:
            node.children.append(self.comment())
        if self.current_token() and self.current_token().type == Lexeme.NEWLINE:
            node.children.append(self.consume_tokens(expected=Lexeme.NEWLINE))
            node.children.append(self.comment_body())
        return node

    # <comment> ::= COMMENT_IDENTIFIER
    def comment(self) -> Node:
        node = Node("comment")
        node.children.append(self.consume_tokens(expected=Lexeme.COMMENT_IDENTIFIER))
        return node