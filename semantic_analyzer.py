from model.lexeme import Lexeme
from model.token import Token

class SemanticAnalyzer:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table

    def analyze(self, node):
        # Dispatch based on node type
        method_name = f"visit_{node.value}" # or node.type
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for i, child in enumerate(node.children):
            self.analyze(child)
            # print(f"Analyzing node: {node.value:<20}\t Child {i}: {child.value}")

    def get_terminal(self, node):
        """
        Recursively traverse the parse tree to find the first terminal node.
        """
        if not node.children:  # If there are no children, it's a terminal node
            return node
        else:
            for child in node.children:
                terminal = self.get_terminal(child)
                if terminal:
                    return terminal
        return None

    def get_terminals(self, node):
        """
        Recursively traverse the parse tree to find all terminal nodes.
        """
        terminals = []
        if not node.children:  # If there are no children, it's a terminal node
            terminals.append(node)
        else:
            for child in node.children:
                terminals.extend(self.get_terminals(child))
        return terminals
    
    # Specific visit methods for different node types
    def visit_declaration(self, node):
        """
        Visit an I_HAS_A node in the parse tree.
            > Child 0: Token for I HAS A
            > Child 1: Token for variable name
            > Child 2: Token for ITZ    (optional)
            > Child 3: Node for value   (optional)
        """
        variable_node = node.children[1].value

        # Check if the variable already exists in the symbol table
        if self.symbol_table.exists(variable_node.lexeme):
            print(f"Error: Variable '{variable_node.lexeme}' already declared.")
            return
        
        if len(node.children) > 2:
            value_node = self.get_terminal(node.children[3]).value
            self.symbol_table.add(variable_node.lexeme, variable_node.type, value_node.lexeme, value_node.type)
        else:
            self.symbol_table.add(variable_node.lexeme, variable_node.type, None, None)

    def visit_loop(self, node):
        """
        Visit a loop node in the parse tree.
            >> Child 0: IM IN YR 
            >> Child 1: loopident
            >> Child 2: <loop_action> 
            >> Child 3: YR 
            >> Child 4: varident 
            >> Child 5: <loop_cond> 
            >> Child 6: <linebreak> 
            >> Child 7: <statement_list> 
            >> Child 8: <linebreak> 
            >> Child 9: IM OUTTA YR 
            >> Child 10: loopident
        """
        # Analyze the loop condition and body
        loop_identifier     = node.children[1].value
        loop_identifier_end = node.children[10].value
        loop_variable = node.children[4].value

        # Check if the loop identifier already exists in the symbol table
        if self.symbol_table.exists(loop_identifier.lexeme):
            print(f"Error: Loop identifier '{loop_identifier.lexeme}' already declared.")
            return
        # Check if the loop identifier at the end matches the one at the beginning
        if loop_identifier.lexeme != loop_identifier_end.lexeme:
            print(f"Error: Loop identifier '{loop_identifier_end.lexeme}' does not match the starting identifier '{loop_identifier.lexeme}'.")
            return
        # Check if loop variable is declared before the loop
        if not self.symbol_table.exists(loop_variable.lexeme):
            print(f"Error: Loop variable '{loop_variable.lexeme}' is not declared before the loop.")
            return

        loop_variable_info = self.symbol_table.get(loop_variable.lexeme)
        # Check if the loop variable is of type NUMBR or NUMBAR
        if loop_variable_info['value_type'] not in [Lexeme.NUMBR_LITERAL, Lexeme.NUMBAR_LITERAL]:
            print(f"Error: Loop variable '{loop_variable_info['value_type']}' must be of type NUMBR or NUMBAR.")
            return

        # Add the loop variable to the symbol table with its type and initial value
        self.symbol_table.add(loop_identifier.lexeme, loop_identifier.type, None, None)

        # Analyze the loop condition and body
        self.analyze(node.children[2])  # Analyze the loop condition
        self.analyze(node.children[5])  # Analyze the loop body
        self.analyze(node.children[7])  # Analyze the statement list inside the loop

    # <func_def> ::= HOW IZ I funcident <linebreak> <statement_list> IF U SAY SO | 
    #                HOW IZ I funcident <func_params> <linebreak> <statement_list> IF U SAY SO
    def visit_func_def(self, node):
        """
        Visit a function definition node in the parse tree.
            >> Child 0: HOW IZ I
            >> Child 1: funcident
            >> Child _/2: <func_params> (optional)
            >> Child 2/3: <linebreak>
            >> Child 3/4: <statement_list>
            >> Child 4/5: IF U SAY SO
        """
        func_identifier = node.children[1].value

        # Check if the function identifier already exists in the symbol table
        if self.symbol_table.exists(func_identifier.lexeme):
            print(f"Error: Function identifier '{func_identifier.lexeme}' already declared.")
            return

        # Analyze the function parameters if they exist
        if len(node.children) == 6:  # Function has parameters
            function_parameters_node = node.children[2]
            params = self.analyze(function_parameters_node)  # Analyze the function parameter list
            self.symbol_table.add(func_identifier.lexeme, func_identifier.type, None, None, 
                                  parameters=params, return_type=None)
        else:  # Function has no parameters
            self.symbol_table.add(func_identifier.lexeme, func_identifier.type, None, None, 
                                  parameters=[], return_type=None)
        # Analyze the function body (statement list)
        self.analyze(node.children[4])  # Analyze the statement list inside the function

    # <func_params> ::= YR varident | YR varident AN <func_params>
    def visit_func_params(self, node):
        """
        Visit a function parameters node in the parse tree.
            >> Child 0: YR
            >> Child 1: varident
            >> Child 2: AN (optional)
            >> Child 3: <func_params> (optional)
        """
        params = []
        var_ident_node = node.children[1].value
        params.append(var_ident_node)
        if len(node.children) > 2:
            # Recursively analyze the next parameter
            params.extend(self.visit_func_params(node.children[3]))
        return params

    # <func_call> ::= I IZ funcident MKAY | I IZ funcident <call_args> MKAY
    def visit_func_call(self, node):
        """
        Visit a function call node in the parse tree.
            >> Child 0: I IZ
            >> Child 1: funcident
            >> Child _/2: <call_args> (optional)
            >> Child 2/3: MKAY
        """
        func_identifier = node.children[1].value

        # Check if the function identifier exists in the symbol table
        if not self.symbol_table.exists(func_identifier.lexeme):
            print(f"Error: Function identifier '{func_identifier.lexeme}' is not declared.")
            return
        
        function_info = self.symbol_table.get(func_identifier.lexeme)

        args = []
        # Analyze the function call arguments if they exist
        if len(node.children) == 4:  # Function call has arguments
            function_arguments_node = node.children[2]
            args = self.analyze(function_arguments_node)  # Analyze the function argument list

        # Check if the type and number of arguments match the function definition
        if len(args) != len(function_info['parameters']):
            print(f"Error: Function '{func_identifier.lexeme}' expects {len(function_info['parameters'])} arguments, but {len(args)} were provided.")
            return

    def visit_call_args(self, node):
        """
        Visit a function call arguments node in the parse tree.
            >> Child 0: <expression>
            >> Child 1: AN (optional)
            >> Child 2: <call_args> (optional)
        """
        if len(node.children) == 0:
            return []
        
        params = []
        var_ident_node = node.children[1].value
        params.append(var_ident_node)
        if len(node.children) > 2:
            # Recursively analyze the next parameter
            params.extend(self.visit_func_params(node.children[3]))
        return params

    # Conditional statements
    # <conditional> ::= O RLY? <linebreak> YA RLY <linebreak> <statement_list> <mebbe_blocks> <no_wai_block> OIC

    # Switch statements
    # <switch> ::= WTF? <linebreak> <case_blocks> <default_block> OIC

    # <case_blocks> ::= OMG <literal> <linebreak> <statement_list> | OMG <literal> <linebreak> <statement_list> <case_blocks>

    # Assignment
    # <assignment> ::= varident R <expression>

    # Arithmetic operations
    # <arithmetic_expr> ::= SUM OF <expression> AN <expression> | DIFF OF <expression> AN <expression> | PRODUKT OF <expression> AN <expression> | QUOSHUNT OF <expression> AN <expression> | MOD OF <expression> AN <expression> | BIGGR OF <expression> AN <expression> | SMALLR OF <expression> AN <expression>

    # Comparison operations
    # <comparison_expr> ::= BOTH SAEM <expression> AN <expression> | DIFFRINT <expression> AN <expression>

    # Loop Condition
    # <loop_cond> ::= TIL <expression> | WILE <expression> | ε67

    # Typecasting
    # <typecast_stmt> ::= varident IS NOW A type