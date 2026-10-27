from model.lexeme import Lexeme
from model.token import Token
from model.node import Node

class Parser():
    """
    Creates a parse tree from a list of tokens using recursive descent parsing.

    Citation:
    - Spivak, R. (2015). Let's build a simple interpreter, part 7. https://ruslanspivak.com/lsbasi-part7/
    """
    STATEMENT_STARTERS = (
        Lexeme.VISIBLE, Lexeme.GIMMEH,
        Lexeme.IDENTIFIER,                      # assignment, IS NOW A, bare variable
        Lexeme.O_RLY, Lexeme.WTF, Lexeme.IM_IN_YR,
        Lexeme.FOUND_YR, Lexeme.I_IZ,
        Lexeme.BTW, Lexeme.OBTW, Lexeme.GTFO,
        Lexeme.NUMBR_LITERAL, Lexeme.NUMBAR_LITERAL, Lexeme.YARN_LITERAL, Lexeme.TROOF_LITERAL,
        Lexeme.SUM_OF, Lexeme.DIFF_OF, Lexeme.PRODUKT_OF, Lexeme.QUOSHUNT_OF,
        Lexeme.MOD_OF, Lexeme.BIGGR_OF, Lexeme.SMALLR_OF, Lexeme.BOTH_OF,
        Lexeme.EITHER_OF, Lexeme.WON_OF, Lexeme.NOT, Lexeme.ANY_OF, Lexeme.ALL_OF,
        Lexeme.BOTH_SAEM, Lexeme.DIFFRINT, Lexeme.SMOOSH, Lexeme.MAEK
    )

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens        # List of tokens
        self.pos = 0                # Current position of the token that is parsed

        self.in_function = False    # currently parsing a function body
        self.in_variadic = False    # currently inside ALL OF / ANY OF
        self.in_smoosh = False      # currently inside SMOOSH
        self.mkay_depth = 0         # enclosing constructs that own a closing MKAY

    def current_token(self) -> Token | None:
        """
        Returns the current token or None if at the end of the token list.
        """
        if self.pos < len(self.tokens):     # Return the current token if within bounds
            return self.tokens[self.pos]
        return None

    def peek_token(self, offset: int = 1) -> Token | None:
        """
        Returns the token 'offset' positions ahead or None if out of range.
        """
        # Check if the position plus offset is within the bounds of the token list
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return None

    def consume_tokens(
            self,
            expected: Token|None = None,
            convert:  Token|None = None,
            optional: bool = False
        ) -> Node:
        """
        Consumes the current token and returns a Node containing it.
        If 'expected' is provided, checks if the current token matches it.
        If 'convert' is provided, changes the token type to 'convert' before returning.
        """
        token = self.current_token()    # Get the current token
        if not token:                   # If there is none, raise an error
            if not optional:
                raise SyntaxError("Unexpected end of input encountered.")
        if expected and token.type != expected: # If it is not expected, raise an error
            if not optional:
                raise SyntaxError(f"Expected {expected}, got {token.type} ({token.lexeme})")
        if convert:                             # If a conversion type is provided, change the token type to it
            token.type = convert
        self.pos += 1                           # Move to the next token
        return Node(token)                      # Return a Node containing the consumed token

    def parse(self) -> Node:
        """
        Starts the parsing process and returns the root of the parse tree.
        """
        tree = self.program()                   # Get the tree from the program rule
        if self.pos < len(self.tokens):         # If there are still tokens left unparsed, raise an error
            raise SyntaxError("Unexpected characters at end of input {}".format(self.tokens[self.pos:]))
        return tree

    # Production rules follow the CFG in the Backus Norm Form for LOLCODE
    # <program> ::= <outer_blocks> HAI <end_of_line> <variables_dec> <statement_list> KTHXBYE <outer_blocks>
    def program(self) -> Node:
        node = Node("program")
        node.children.append(self.outer_blocks())
        node.children.append(self.consume_tokens(expected=Lexeme.HAI))      # HAI
        node.children.append(self.end_of_line())
        node.children.append(self.variables_dec())
        node.children.append(self.statement_list())
        node.children.append(self.consume_tokens(expected=Lexeme.KTHXBYE))  # KTHXBYE
        node.children.append(self.outer_blocks())
        return node

    # <outer_blocks> ::= <func_def> <end_of_line> <outer_blocks> | <comments> <outer_blocks> | <linebreak> <outer_blocks> | ε
    def outer_blocks(self) -> Node:
        node = Node("outer_blocks")
        # <func_def> <end_of_line> <outer_blocks>
        if self.current_token() and self.current_token().type == Lexeme.HOW_IZ_I:   # If first child is func_def
            node.children.append(self.func_def())
            node.children.append(self.end_of_line())
            node.children.append(self.outer_blocks())
        # <comments> <outer_blocks> 
        elif self.current_token() and self.current_token().type in [Lexeme.BTW, Lexeme.OBTW]:
            node.children.append(self.comments())
            node.children.append(self.outer_blocks())
        # <linebreak> <outer_blocks>
        elif self.current_token() and self.current_token().type == Lexeme.NEWLINE:
            node.children.append(self.linebreak())
            node.children.append(self.outer_blocks())   # a function may follow the blank lines
        else:
            pass # Epsilon
        return node

    # <statement_list> ::= <statement> <end_of_line> <statement_list> | <newline> <statement_list> | ε
    def statement_list(self) -> Node:
        node = Node("statement_list")   # Create a new node for the statement list
        token = self.current_token()    # Get the current token

        if token and token.type == Lexeme.I_HAS_A and not self.in_function:     # If I HAS A is found outside a function, raise an error
            raise SyntaxError(f"Variables must be declared inside the WAZZUP ... BUHBYE section ({token.lexeme})")
        if token and token.type == Lexeme.HOW_IZ_I:                             # If HOW IZ I is found inside the program body, raise an error
            raise SyntaxError("Functions must be defined before HAI or after KTHXBYE, not inside the program body")

        starters = self.STATEMENT_STARTERS
        if self.in_function:        # if inside a function body, allow variable declarations
            starters = starters + (Lexeme.I_HAS_A,)

        # <statement> <end_of_line> <statement_list> 
        if token and token.type in starters:
            node.children.append(self.statement())
            node.children.append(self.end_of_line())    # one statement per line
            node.children.append(self.statement_list())
        # <newline> <statement_list> 
        elif token and token.type == Lexeme.NEWLINE:
            node.children.append(self.consume_tokens(expected=Lexeme.NEWLINE))  # newline
            node.children.append(self.statement_list())
        else:
            pass # Epsilon
        return node

    # <statement> ::= <print> | <declaration> | <assignment> | <input> | <conditional> | <switch> | <loop> | <return_stmt> | <typecast_stmt> | <inline_comment> | <multi_comment> | <expression> | GTFO
    def statement(self) -> Node:
        node = Node("statement")            # Create a new node for the statement
        token = self.current_token()        # Get the current token

        if token and token.type == Lexeme.VISIBLE:
            node.children.append(self.print())
        elif token and token.type == Lexeme.I_HAS_A:
            # statement_list only lets this through inside a function body
            node.children.append(self.declaration())
        elif token and token.type == Lexeme.IDENTIFIER:
            next_token = self.peek_token()
            if next_token and next_token.type == Lexeme.R:
                node.children.append(self.assignment())
            elif next_token and next_token.type == getattr(Lexeme, 'IS_NOW_A', None):
                node.children.append(self.typecast_stmt())
            else:
                node.children.append(self.expression())
        elif token and token.type == Lexeme.GIMMEH:
            node.children.append(self.input())
        elif token and token.type == Lexeme.O_RLY:
            node.children.append(self.conditional())
        elif token and token.type == Lexeme.WTF:
            node.children.append(self.switch())
        elif token and token.type == Lexeme.IM_IN_YR:
            node.children.append(self.loop())
        elif token and token.type == Lexeme.FOUND_YR:
            node.children.append(self.return_stmt())
        elif token and token.type == Lexeme.BTW:
            node.children.append(self.inline_comment())
        elif token and token.type == Lexeme.OBTW:
            node.children.append(self.multi_comment())
        elif token and token.type == Lexeme.GTFO:
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

    # <literal> ::= NUMBR_LITERAL | NUMBAR_LITERAL | YARN_LITERAL | TROOF_LITERAL
    def literal(self) -> Node:
        node = Node("literal")
        if self.current_token() and self.current_token().type in [Lexeme.NUMBR_LITERAL, Lexeme.NUMBAR_LITERAL, Lexeme.YARN_LITERAL, Lexeme.TROOF_LITERAL]:
            node.children.append(self.consume_tokens(expected=self.current_token().type))
        else:
            raise SyntaxError("Expected a literal")
        return node

    # <type> ::= TYPE_LITERAL (YARN | NUMBR | NUMBAR | TROOF | NOOB)
    def type(self) -> Node:
        node = Node("type")
        if self.current_token() and self.current_token().type == Lexeme.TYPE_LITERAL:
            node.children.append(self.consume_tokens(expected=self.current_token().type))
        else:
            raise SyntaxError(f"Expected a type token, got {self.current_token()}")
        return node

    # <variables_dec> ::= WAZZUP <end_of_line> <vars> BUHBYE <end_of_line> | ε
    def variables_dec(self) -> Node:
        node = Node("variables_dec")
        if self.current_token() and self.current_token().type == Lexeme.WAZZUP:
            node.children.append(self.consume_tokens(expected=Lexeme.WAZZUP))  # WAZZUP
            node.children.append(self.end_of_line())
            node.children.append(self.vars())
            node.children.append(self.consume_tokens(expected=Lexeme.BUHBYE))  # BUHBYE
            node.children.append(self.end_of_line())
        else:
            pass # Epsilon
        return node

    # <vars> ::= <declaration> <end_of_line> <vars> | <newline> <vars> | <linebreak-with-BTW> <vars> | <multi_comment> <end_of_line> <vars> | ε
    def vars(self) -> Node:
        node = Node("vars")
        token = self.current_token()
        if token and token.type == Lexeme.I_HAS_A:
            node.children.append(self.declaration())
            node.children.append(self.end_of_line())
            node.children.append(self.vars())
        elif token and token.type == Lexeme.NEWLINE:
            node.children.append(self.consume_tokens(expected=Lexeme.NEWLINE))  # newline
            node.children.append(self.vars())
        elif token and token.type == Lexeme.BTW:
            # full-line BTW comment inside WAZZUP
            node.children.append(self.linebreak())
            node.children.append(self.vars())
        # <multi_comment> <end_of_line> <vars> | <multi_comment> <vars> 
        elif token and token.type == Lexeme.OBTW:
            node.children.append(self.multi_comment())
            node.children.append(self.end_of_line())
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
        node = Node("assignment")       # Create a new node for the assignment statement
        node.children.append(self.consume_tokens(expected=Lexeme.IDENTIFIER, convert=Lexeme.VARIABLE_IDENTIFIER))  # VARIABLE_IDENTIFIER
        node.children.append(self.consume_tokens(expected=Lexeme.R))  # R
        node.children.append(self.expression())
        return node

    # <input> ::= GIMMEH varident
    def input(self) -> Node:
        node = Node("input")            # Create a new node for the input statement
        node.children.append(self.consume_tokens(expected=Lexeme.GIMMEH))  # GIMMEH
        node.children.append(self.consume_tokens(expected=Lexeme.IDENTIFIER, convert=Lexeme.VARIABLE_IDENTIFIER))  # VARIABLE_IDENTIFIER
        return node

    # <expression> ::= <operand> | <arithmetic_expr> | <boolean_expr> | <comparison_expr> | <concatenation_expr> | <typecast_expr> | <func_call>
    def expression(self) -> Node:
        node = Node("expression")       # Create a new node for the expression
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
        node = Node("operand")          # Create a new node for the operand
        if self.current_token() and self.current_token().type == Lexeme.IDENTIFIER:
            node.children.append(self.consume_tokens(expected=Lexeme.IDENTIFIER, convert=Lexeme.VARIABLE_IDENTIFIER))  # VARIABLE_IDENTIFIER
        else:
            node.children.append(self.literal())
        return node

    # <arithmetic_expr> ::= SUM OF <expression> AN <expression> | DIFF OF <expression> AN <expression> | PRODUKT OF <expression> AN <expression> | QUOSHUNT OF <expression> AN <expression> | MOD OF <expression> AN <expression> | BIGGR OF <expression> AN <expression> | SMALLR OF <expression> AN <expression>
    def arithmetic_expr(self) -> Node:
        node = Node("arithmetic_expr")  # Create a new node for the arithmetic expression
        # Check if the current token is an arithmetic operator and parse accordingly
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

    # <boolean_expr> ::= BOTH OF <expression> AN <expression> | EITHER OF <expression> AN <expression> | WON OF <expression> AN <expression> | NOT <expression> | ANY OF <expr_list> MKAY | ALL OF <expr_list> MKAY
    def boolean_expr(self) -> Node:
        node = Node("boolean_expr")     # Create a new node for the boolean expression
        # Check if the current token is a boolean operator and parse accordingly
        if self.current_token() and self.current_token().type in [
            Lexeme.BOTH_OF, Lexeme.EITHER_OF, Lexeme.WON_OF
        ]:
            node.children.append(self.consume_tokens(expected=self.current_token().type))  # Operation
            node.children.append(self.expression())
            node.children.append(self.consume_tokens(expected=Lexeme.AN))  # AN
            node.children.append(self.expression())
        # Check if the current token is NOT and parse accordingly
        elif self.current_token() and self.current_token().type == Lexeme.NOT:
            node.children.append(self.consume_tokens(expected=Lexeme.NOT))  # NOT
            node.children.append(self.expression())
        # Check if the current token is ANY OF or ALL OF and parse accordingly
        elif self.current_token() and self.current_token().type in [Lexeme.ANY_OF, Lexeme.ALL_OF]:
            # ALL OF / ANY OF cannot be nested in each other or themselves
            if self.in_variadic:
                raise SyntaxError(
                    f"ALL OF / ANY OF cannot be nested inside another ALL OF / ANY OF ({self.current_token().lexeme})"
                )
            node.children.append(self.consume_tokens(expected=self.current_token().type))  # ANY OF, ALL OF
            self.in_variadic = True
            self.mkay_depth += 1
            # Try to append the expr_list, and ensure that in_variadic is reset to False afterwards
            # Make sure that in_variadic flag is reset even if expr_list raises an exception
            try:
                node.children.append(self.expr_list())
            finally:
                # Clear the in_variadic flag to False after parsing the expr_list
                self.in_variadic = False
                self.mkay_depth -= 1
            node.children.append(self.consume_tokens(expected=Lexeme.MKAY))  # MKAY
        else:
            raise SyntaxError("Unexpected token in boolean expression")
        return node

    # <expr_list> ::= <expression> | <expression> AN <expr_list>
    def expr_list(self) -> Node:
        node = Node("expr_list")                # Create a new node for the expression list
        node.children.append(self.expression()) # Append the first expression to the list
        # An 'AN YR' belongs to an enclosing function call/definition, not to this list
        next_token = self.peek_token()          # Get the next token to check if it is 'AN YR'
        if (self.current_token() and self.current_token().type == Lexeme.AN
                and not (next_token and next_token.type == Lexeme.YR)):
            node.children.append(self.consume_tokens(expected=Lexeme.AN))  # AN
            node.children.append(self.expr_list())
        return node

    # <comparison_expr> ::= BOTH SAEM <expression> AN <expression> | DIFFRINT <expression> AN <expression>
    def comparison_expr(self) -> Node:
        node = Node("comparison_expr")      # Create a new node for the comparison expression
        # Check if the current token is BOTH SAEM or DIFFRINT, and parse accordingly
        if self.current_token() and self.current_token().type in [Lexeme.BOTH_SAEM, Lexeme.DIFFRINT]:
            node.children.append(self.consume_tokens(expected=self.current_token().type))  # BOTH SAEM or DIFFRINT
            node.children.append(self.expression())
            node.children.append(self.consume_tokens(expected=Lexeme.AN))  # AN
            node.children.append(self.expression())
        else:
            raise SyntaxError("Unexpected token in comparison expression")
        return node

    # <concatenation_expr> ::= SMOOSH <expr_list> MKAY | SMOOSH <expr_list>
    def concatenation_expr(self) -> Node:
        node = Node("concatenation_expr")   # Create a new node for the concatenation expression
        if self.in_smoosh:                  # If already inside a SMOOSH, raise an error to prevent nesting
            raise SyntaxError("SMOOSH cannot be nested inside another SMOOSH")
        # SMOOSH <expr_list> MKAY | SMOOSH <expr_list>
        node.children.append(self.consume_tokens(expected=Lexeme.SMOOSH))  # SMOOSH
        self.in_smoosh = True
        # Try to append the expr_list, and ensure that in_smoosh is reset to False afterwards
        # Make sure that in_smoosh flag is reset even if expr_list raises an exception
        try:
            node.children.append(self.expr_list())
        finally:
            # Reset the in_smoosh flag to False after parsing the expr_list
            self.in_smoosh = False
        # Only take an MKAY if no enclosing construct is waiting for it
        if self.mkay_depth == 0 and self.current_token() and self.current_token().type == Lexeme.MKAY:
            node.children.append(self.consume_tokens(expected=Lexeme.MKAY))  # MKAY
        return node

    # <typecast_expr> ::= MAEK <expression> A type | MAEK <expression> type
    def typecast_expr(self) -> Node:
        node = Node("typecast_expr")    # Create a new node for the typecast expression
        node.children.append(self.consume_tokens(expected=Lexeme.MAEK))  # MAEK
        node.children.append(self.expression())
        # Check if an 'A' token is present, indicating a typecast
        if self.current_token() and self.current_token().type == Lexeme.A:
            node.children.append(self.consume_tokens(expected=Lexeme.A))  # A
        node.children.append(self.type())
        return node

    # <typecast_stmt> ::= varident IS NOW A type
    def typecast_stmt(self) -> Node:
        node = Node("typecast_stmt")    # Create a new node for the typecast statement
        node.children.append(self.consume_tokens(expected=Lexeme.IDENTIFIER, convert=Lexeme.VARIABLE_IDENTIFIER))  # VARIABLE_IDENTIFIER
        node.children.append(self.consume_tokens(expected=Lexeme.IS_NOW_A))  # IS NOW A (lexer bundles this into 1 token)
        node.children.append(self.type())
        return node

    # <conditional> ::= O RLY? <end_of_line> YA RLY <end_of_line> <statement_list> <mebbe_blocks> <no_wai_block> OIC
    def conditional(self) -> Node:
        node = Node("conditional")      # Create a new node for the conditional statement
        node.children.append(self.consume_tokens(expected=Lexeme.O_RLY))  # O RLY
        node.children.append(self.end_of_line())
        node.children.append(self.consume_tokens(expected=Lexeme.YA_RLY))  # YA RLY
        node.children.append(self.end_of_line())
        node.children.append(self.statement_list())
        node.children.append(self.mebbe_blocks())
        node.children.append(self.no_wai_block())
        node.children.append(self.consume_tokens(expected=Lexeme.OIC))  # OIC
        return node

    # <mebbe_blocks> ::= MEBBE <expression> <end_of_line> <statement_list> <mebbe_blocks> | ε
    def mebbe_blocks(self) -> Node:
        node = Node("mebbe_blocks")     # Create a new node for the MEBBE blocks
        # Parse the MEBBE blocks, if they exist
        if self.current_token() and self.current_token().type == Lexeme.MEBBE:
            node.children.append(self.consume_tokens(expected=Lexeme.MEBBE))
            node.children.append(self.expression())
            node.children.append(self.end_of_line())
            node.children.append(self.statement_list())
            node.children.append(self.mebbe_blocks())
        return node

    # <no_wai_block> ::= NO WAI <end_of_line> <statement_list> | ε
    def no_wai_block(self) -> Node:
        node = Node("no_wai_block")     # Create a new node for the NO WAI block
        # Parse the NO WAI block, if it exists
        if self.current_token() and self.current_token().type == Lexeme.NO_WAI:
            node.children.append(self.consume_tokens(expected=Lexeme.NO_WAI))
            node.children.append(self.end_of_line())
            node.children.append(self.statement_list())
        return node

    # <switch> ::= WTF? <end_of_line> <case_blocks> <default_block> OIC     
    def switch(self) -> Node:
        node = Node("switch")           # Create a new node for the switch statement
        node.children.append(self.consume_tokens(expected=Lexeme.WTF))
        node.children.append(self.end_of_line())
        # Ensure that there is at least one OMG case after WTF?
        # if not, raise a SyntaxError
        if not (self.current_token() and self.current_token().type == Lexeme.OMG):
            raise SyntaxError(f"Expected at least one OMG case after WTF?, got {self.current_token()}")
        node.children.append(self.case_blocks())
        node.children.append(self.default_block())
        node.children.append(self.consume_tokens(expected=Lexeme.OIC))  # OIC
        return node

    # <case_blocks> ::= OMG <literal> <end_of_line> <statement_list> <case_blocks> | ε
    def case_blocks(self) -> Node:
        node = Node("case_blocks")      # Create a new node for the case blocks
        # Parse the case blocks, if they exist
        if self.current_token() and self.current_token().type == Lexeme.OMG:
            node.children.append(self.consume_tokens(expected=Lexeme.OMG))
            node.children.append(self.literal())
            node.children.append(self.end_of_line())
            node.children.append(self.statement_list())
            node.children.append(self.case_blocks())
        return node

    # <default_block> ::= OMGWTF <end_of_line> <statement_list> | ε
    def default_block(self) -> Node:
        node = Node("default_block")    # Create a new node for the default block
        if self.current_token() and self.current_token().type == Lexeme.OMGWTF:
            node.children.append(self.consume_tokens(expected=Lexeme.OMGWTF))
            node.children.append(self.end_of_line())
            node.children.append(self.statement_list())
        return node

    # <loop> ::= IM IN YR loopident <loop_action> YR varident <loop_cond> <end_of_line> <statement_list> IM OUTTA YR loopident
    def loop(self) -> Node:
        node = Node("loop")       # Create a new node for the loop
        node.children.append(self.consume_tokens(expected=Lexeme.IM_IN_YR))  # IM IN YR
        open_label = self.current_token()
        node.children.append(self.consume_tokens(expected=Lexeme.IDENTIFIER, convert=Lexeme.LOOP_IDENTIFIER))
        node.children.append(self.loop_action())
        node.children.append(self.consume_tokens(expected=Lexeme.YR))  # YR
        node.children.append(self.consume_tokens(expected=Lexeme.IDENTIFIER, convert=Lexeme.VARIABLE_IDENTIFIER))  # VARIABLE_IDENTIFIER
        node.children.append(self.loop_cond())
        node.children.append(self.end_of_line())
        node.children.append(self.statement_list())
        node.children.append(self.linebreak())
        node.children.append(self.consume_tokens(expected=Lexeme.IM_OUTTA_YR))  # IM OUTTA YR
        close_label = self.current_token()
        node.children.append(self.consume_tokens(expected=Lexeme.IDENTIFIER, convert=Lexeme.LOOP_IDENTIFIER))
        # Check if the opening and closing loop labels match, raising a SyntaxError if they do not
        if open_label.lexeme != close_label.lexeme:
            raise SyntaxError(
                f"Loop label mismatch: IM IN YR {open_label.lexeme} closed by IM OUTTA YR {close_label.lexeme}"
            )
        return node

    # <loop_action> ::= UPPIN | NERFIN
    def loop_action(self) -> Node:
        node = Node("loop_action")      # Create a new node for the loop action
        if self.current_token() and self.current_token().type in [Lexeme.UPPIN, Lexeme.NERFIN]:
            node.children.append(self.consume_tokens(expected=self.current_token().type))
        else:
            raise SyntaxError("Expected loop action")
        return node

    # <loop_cond> ::= TIL <expression> | WILE <expression> | ε
    def loop_cond(self) -> Node:
        node = Node("loop_cond")        # Create a new node for the loop condition
        # Parse the loop condition, if it exists
        if self.current_token() and self.current_token().type in [Lexeme.TIL, Lexeme.WILE]:
            node.children.append(self.consume_tokens(expected=self.current_token().type))
            node.children.append(self.expression())
        return node

    # <func_def> ::= HOW IZ I funcident <linebreak> <statement_list> IF U SAY SO | HOW IZ I funcident <func_params> <linebreak> <statement_list> IF U SAY SO
    def func_def(self) -> Node:
        node = Node("func_def")         # Create a new node for the function definition
        # HOW IZ I funcident
        node.children.append(self.consume_tokens(expected=Lexeme.HOW_IZ_I))
        node.children.append(self.consume_tokens(expected=Lexeme.IDENTIFIER, convert=Lexeme.FUNCTION_IDENTIFIER))
        # Optional function parameters
        if self.current_token() and self.current_token().type == Lexeme.YR:
            node.children.append(self.func_params())
        # <linebreak> <statement_list>
        node.children.append(self.end_of_line())
        previous = self.in_function
        self.in_function = True
        # Parse the statement list inside the function body, ensuring that the in_function flag is restored afterward
        try:
            node.children.append(self.statement_list())
        finally:
            # Restore the previous state of the in_function flag after parsing the function body
            self.in_function = previous
        node.children.append(self.consume_tokens(expected=Lexeme.IF_U_SAY_SO))  # IF U SAY SO
        return node

    # <func_params> ::= YR varident | YR varident AN <func_params>
    def func_params(self) -> Node:
        node = Node("func_params")      # Create a new node for the function parameters
        node.children.append(self.consume_tokens(expected=Lexeme.YR))       # YR
        node.children.append(self.consume_tokens(expected=Lexeme.IDENTIFIER, convert=Lexeme.VARIABLE_IDENTIFIER))  # VARIABLE_IDENTIFIER
        if self.current_token() and self.current_token().type == Lexeme.AN:
            node.children.append(self.consume_tokens(expected=Lexeme.AN))   # AN
            node.children.append(self.func_params())
        return node

    # <return_stmt> ::= FOUND YR <expression>
    def return_stmt(self) -> Node:
        node = Node("return_stmt")      # Create a new node for the return statement
        node.children.append(self.consume_tokens(expected=Lexeme.FOUND_YR))
        node.children.append(self.expression())
        return node

    # <func_call> ::= I IZ funcident MKAY | I IZ funcident <call_args> MKAY
    def func_call(self) -> Node:
        node = Node("func_call")        # Create a new node for the function call
        # I IZ funcident
        node.children.append(self.consume_tokens(expected=Lexeme.I_IZ))
        node.children.append(self.consume_tokens(expected=Lexeme.IDENTIFIER, convert=Lexeme.FUNCTION_IDENTIFIER))

        # Arguments are their own expression context
        # reset nesting flags, and tell SMOOSH/ALL OF that this call owns the closing MKAY.
        saved_variadic, saved_smoosh = self.in_variadic, self.in_smoosh
        self.in_variadic = self.in_smoosh = False
        self.mkay_depth += 1
        # If the next token is YR, parse the call arguments
        try:
            if self.current_token() and self.current_token().type == Lexeme.YR:
                node.children.append(self.call_args())
        finally:
            # Restore the previous state of the parser after parsing the call arguments
            self.mkay_depth -= 1
            self.in_variadic, self.in_smoosh = saved_variadic, saved_smoosh

        node.children.append(self.consume_tokens(expected=Lexeme.MKAY))  # MKAY
        return node

    # <call_args> ::= YR <expression> | YR <expression> AN <call_args>
    def call_args(self) -> Node:
        node = Node("call_args")        # Create a new node for the call arguments
        # YR <expression>
        node.children.append(self.consume_tokens(expected=Lexeme.YR))  # YR
        node.children.append(self.expression())
        # Optional AN <call_args>
        if self.current_token() and self.current_token().type == Lexeme.AN:
            node.children.append(self.consume_tokens(expected=Lexeme.AN))
            node.children.append(self.call_args())
        return node

    # <end_of_line> ::= <linebreak>
    def end_of_line(self) -> Node:
        token = self.current_token()    # Get the current token
        # If the current token is not a newline or a comment, raise an error
        if token and token.type not in (Lexeme.NEWLINE, Lexeme.BTW):
            raise SyntaxError(f"Expected end of line, got {token.type} ({token.lexeme})")
        return self.linebreak()

    # <linebreak> ::= <newline> | <inline_comment> <newline> | ε
    def linebreak(self) -> Node:
        node = Node("linebreak")        # Create a new node for the linebreak
        # <inline_comment> <newline>
        if self.current_token() and self.current_token().type == Lexeme.BTW:
            node.children.append(self.inline_comment())
        # <newline>
        if self.current_token() and self.current_token().type == Lexeme.NEWLINE:
            # Consume all \n newlines
            while self.current_token() and self.current_token().type == Lexeme.NEWLINE:
                node.children.append(self.consume_tokens(expected=Lexeme.NEWLINE))
        else:
            pass # Epsilon
        return node

    # <comments> ::= <linebreak> <comments> | <multi_comment> <linebreak> <comments> | ε
    def comments(self) -> Node:
        node = Node("comments")         # Create a new node for the comments
        # <multi_comment> <linebreak> <comments>
        if self.current_token() and self.current_token().type == Lexeme.OBTW:
            node.children.append(self.multi_comment())
            node.children.append(self.linebreak())
            node.children.append(self.comments())
        # <linebreak> <comments> 
        elif self.current_token() and self.current_token().type in [Lexeme.BTW, Lexeme.NEWLINE]:
            node.children.append(self.linebreak())
            node.children.append(self.comments())
        return node

    # <inline_comment> ::= BTW <comment> | BTW
    def inline_comment(self) -> Node:
        node = Node("inline_comment")   # Create a new node for the inline comment
        node.children.append(self.consume_tokens(expected=Lexeme.BTW)) # BTW
        # Optional comment after BTW
        while self.current_token() and self.current_token().type == Lexeme.COMMENT_IDENTIFIER:
            node.children.append(self.comment())
        return node

    # <multi_comment> ::= OBTW [<comment>] newline <comment_body> TLDR [<comment>]
    def multi_comment(self) -> Node:
        node = Node("multi_comment")    # Create a new node for the multi-line comment
        node.children.append(self.consume_tokens(expected=Lexeme.OBTW))
        # Optional comment after OBTW
        while self.current_token() and self.current_token().type == Lexeme.COMMENT_IDENTIFIER:
            node.children.append(self.comment())
        # TODO: Optional NEWLINE
        node.children.append(self.consume_tokens(expected=Lexeme.NEWLINE, optional=True))  # newline
        node.children.append(self.comment_body())
        node.children.append(self.consume_tokens(expected=Lexeme.TLDR))  # TLDR
        # Optional comment after TLDR
        while self.current_token() and self.current_token().type == Lexeme.COMMENT_IDENTIFIER:
            node.children.append(self.comment())
        return node

    # <comment_body> ::= <comment> <newline> <comment_body> | <newline> <comment_body> | ε
    def comment_body(self) -> Node:
        node = Node("comment_body")     # Create a new node for the comment body
        # <comment> <newline> <comment_body> 
        if self.current_token() and self.current_token().type == Lexeme.COMMENT_IDENTIFIER:
            node.children.append(self.comment())
        # <newline> <comment_body> 
        if self.current_token() and self.current_token().type == Lexeme.NEWLINE:
            node.children.append(self.consume_tokens(expected=Lexeme.NEWLINE))
            node.children.append(self.comment_body())
        else:
            pass # Epsilon
        return node

    # <comment> ::= COMMENT_IDENTIFIER
    def comment(self) -> Node:
        node = Node("comment")          # Create a new node for the comment
        node.children.append(self.consume_tokens(expected=Lexeme.COMMENT_IDENTIFIER))
        return node
