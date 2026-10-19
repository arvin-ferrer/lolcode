from model.lexeme import Lexeme
from model.token import Token
from model.node import Node
from model.symbol_table import SymbolTable
import re
class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()  # Initialize a new symbol table for semantic analysis

    def analyze(self, node: Node) -> None:
        # Dispatch based on node type
        method_name = f"visit_{node.value}" # or node.type
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: Node) -> None:
        for i, child in enumerate(node.children):
            self.analyze(child)

    def get_terminal(self, node: Node) -> Node:
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

    def get_terminal_with_parent(self, node: Node, parent: Node|None=None) -> tuple:
        """
        Recursively traverse the parse tree to find the first terminal node and its parent.
        """
        if not node.children:  # If there are no children, it's a terminal node
            return (node, None)
        else:
            for child in node.children:
                terminal, parent = self.get_terminal_with_parent(child, node)
                if terminal:
                    return (terminal, node)
        return (None, None)

    def get_terminals(self, node: Node) -> list[Node]:
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
    def visit_declaration(self, node: Node):
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

    def visit_loop(self, node: Node):
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
    def visit_func_def(self, node: Node):
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
    def visit_func_params(self, node: Node):
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

    def visit_call_args(self, node: Node):
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
    def visit_call_conditional(self, node: Node):
        """
        Visit a conditional statement node in the parse tree.
            >> Child 0: O RLY?
            >> Child 1: <linebreak>
            >> Child 2: YA RLY
            >> Child 3: <linebreak>
            >> Child 4: <statement_list>
            >> Child 5: <mebbe_blocks> (optional)
            >> Child 6: <no_wai_block> (optional)
            >> Child 7: OIC
        """
        # Analyze the statement list for the YA RLY block
        self.analyze(node.children[4])  # Analyze the statement list inside the YA RLY block

        # Analyze the MEBBE blocks if they exist
        if len(node.children) > 5:
            mebbe_blocks_node = node.children[5]
            self.analyze(mebbe_blocks_node)  # Analyze the MEBBE blocks

        # Analyze the NO WAI block if it exists
        if len(node.children) > 6:
            no_wai_block_node = node.children[6]
            self.analyze(no_wai_block_node)  # Analyze the NO WAI block

    def visit_mebbe_blocks(self, node: Node):
        """
        Visit a MEBBE blocks node in the parse tree.
            >> Child 0: MEBBE
            >> Child 1: <expression>
            >> Child 2: <linebreak>
            >> Child 3: <statement_list>
            >> Child 4: <mebbe_blocks> (optional)
        """
        if len(node.children) < 3:
            return
        # Analyze the statement list for the current MEBBE block
        self.analyze(node.children[3])  # Analyze the statement list inside the current MEBBE block

        # Analyze the next MEBBE block if it exists
        if len(node.children) > 4:
            mebbe_blocks_node = node.children[4]
            self.analyze(mebbe_blocks_node)  # Analyze the next MEBBE block

    def visit_no_wai_block(self, node: Node):
        """
        Visit a NO WAI block node in the parse tree.
            >> Child 0: NO WAI
            >> Child 1: <linebreak>
            >> Child 2: <statement_list>
        """
        if len(node.children) < 2:
            return
        # Analyze the statement list for the NO WAI block
        self.analyze(node.children[2])  # Analyze the statement list inside the NO WAI block

    # Switch statements
    # <switch> ::= WTF? <linebreak> <case_blocks> <default_block> OIC
    def visit_switch(self, node: Node):
        """
        Visit a switch statement node in the parse tree.
            >> Child 0: WTF?
            >> Child 1: <linebreak>
            >> Child 2: <case_blocks>
            >> Child 3: <default_block> (optional)
            >> Child 4: OIC
        """
        # Analyze the case blocks
        self.analyze(node.children[2])  # Analyze the case blocks

        # Analyze the default block if it exists
        if len(node.children) > 3:
            default_block_node = node.children[3]
            self.analyze(default_block_node)  # Analyze the default block
        
    # <case_blocks> ::= OMG <literal> <linebreak> <statement_list> | OMG <literal> <linebreak> <statement_list> <case_blocks>
    def visit_case_blocks(self, node: Node):
        """
        Visit a case blocks node in the parse tree.
            >> Child 0: OMG
            >> Child 1: <literal>
            >> Child 2: <linebreak>
            >> Child 3: <statement_list>
            >> Child 4: <case_blocks> (optional)
        """
        # Analyze the statement list for the current case block
        self.analyze(node.children[3])  # Analyze the statement list inside the current case block

        # Analyze the next case block if it exists
        if len(node.children) > 4:
            case_blocks_node = node.children[4]
            self.analyze(case_blocks_node)  # Analyze the next case block
        
    # Assignment
    # <assignment> ::= varident R <expression>
    def visit_assignment(self, node: Node):
        """
        Visit an assignment node in the parse tree.
            >> Child 0: varident
            >> Child 1: R
            >> Child 2: <expression>
        """
        var_ident_node = node.children[0].value
        expression_node = node.children[2]

        # Check if the variable is declared before assignment
        if not self.symbol_table.exists(var_ident_node.lexeme):
            print(f"Error: Variable '{var_ident_node.lexeme}' is not declared before assignment.")
            return

        # Analyze the expression to get its value and type
        expression_value_node = self.get_terminal(expression_node)
        expression_value = expression_value_node.value
        # Check if the type of the expression matches the type of the variable
        variable_info = self.symbol_table.get(var_ident_node.lexeme)
        if variable_info['value_type'] != expression_value.type:
            print(f"Error: Type mismatch in assignment. Variable '{var_ident_node.lexeme}' is of type '{variable_info['value_type']}', but the expression is of type '{expression_value.type}'.")
            return
        
        # Update the symbol table with the new value and type for the variable
        self.symbol_table.add(var_ident_node.lexeme, var_ident_node.type, expression_value.lexeme, expression_value.type)

    # Arithmetic operations
    # <arithmetic_expr> ::= SUM OF <expression> AN <expression> | DIFF OF <expression> AN <expression> | PRODUKT OF <expression> AN <expression> | QUOSHUNT OF <expression> AN <expression> | MOD OF <expression> AN <expression> | BIGGR OF <expression> AN <expression> | SMALLR OF <expression> AN <expression>
    def visit_arithmetic_expr(self, node: Node):
        """
        Visit an arithmetic expression node in the parse tree.
            >> Child 0: SUM OF | DIFF OF | PRODUKT OF | QUOSHUNT OF | MOD OF | BIGGR OF | SMALLR OF
            >> Child 1: <expression>
            >> Child 2: AN
            >> Child 3: <expression>
        """
        if node.value != 'arithmetic_expr':
            for child in node.children:
                self.visit_arithmetic_expr(child)
            if isinstance(node.value, Token):
                # Typecheck the literal values of the arithmetic expression
                # Implicit type conversion for YARN (string) to NUMBR or NUMBAR is allowed
                # If either operand is of type YARN, we can attempt to convert it to NUMBR or NUMBAR
                if node.value.type == Lexeme.YARN_LITERAL:
                    conv = self.convert_yarn_to_num(node)
                    if conv is None:
                        print(f"Error: Cannot convert operand '{node.value.lexeme}' of type YARN to NUMBR or NUMBAR.")
                        return
                    lex, type = conv
                    node.value.lexeme = lex
                    node.value.type = type
                elif node.value.type not in [Lexeme.NUMBR_LITERAL, Lexeme.NUMBAR_LITERAL]:
                    print(f"Error: Arithmetic operations require operands to be of type NUMBR or NUMBAR. Found type '{node.value.type}'.")
                    return
            return
        # Analyze the left and right expressions
        left_expression_node = node.children[1]
        right_expression_node = node.children[3]

        self.visit_arithmetic_expr(left_expression_node)
        self.visit_arithmetic_expr(right_expression_node)
        return
    
    def convert_yarn_to_num(self, node: Node) -> tuple:
        if out := re.search(r'^"-?\d+"$', node.value.lexeme):
            return node.value.lexeme, Lexeme.NUMBR_LITERAL
        elif out := re.search(r'^"-?\d+\.\d+"$', node.value.lexeme):
            return node.value.lexeme, Lexeme.NUMBAR_LITERAL
        else:
            return None
    # Comparison operations
    # <comparison_expr> ::= BOTH SAEM <expression> AN <expression> | DIFFRINT <expression> AN <expression>
    def visit_comparison_expr(self, node: Node):
        """
        Visit a comparison expression node in the parse tree.
            >> Child 0: BOTH SAEM | DIFFRINT
            >> Child 1: <expression>
            >> Child 2: AN
            >> Child 3: <expression>
        """
        # Analyze the left and right expressions
        left_expression_node = node.children[1]
        right_expression_node = node.children[3]

        left_value_node = self.get_terminal(left_expression_node)
        right_value_node = self.get_terminal(right_expression_node)

        # Calculate the types of the left and right expressions
        if left_value_node.value.type == Lexeme.VARIABLE_IDENTIFIER:
            data = self.symbol_table.get(left_value_node.value.lexeme)
            if data is None:
                print(f"Error: Variable '{left_value_node.value.lexeme}' is not declared before comparison.")
                return
            left_type = data['value_type']
        else:
            left_type = left_value_node.value.type

        if right_value_node.value.type == Lexeme.VARIABLE_IDENTIFIER:
            data = self.symbol_table.get(right_value_node.value.lexeme)
            if data is None:
                print(f"Error: Variable '{right_value_node.value.lexeme}' is not declared before comparison.")
                return
            right_type = data['value_type']
        else:
            right_type = right_value_node.value.type

        # Check if both expressions are of the same type
        if left_type != right_type:
            print(f"Error: Comparison operations require both operands to be of the same type. Found types '{left_value_node.value.type}' and '{right_value_node.value.type}'.")
            return

    # Loop Condition
    # <loop_cond> ::= TIL <expression> | WILE <expression> | ε
    def visit_loop_cond(self, node: Node):
        """
        Visit a loop condition node in the parse tree.
            >> Child 0: TIL | WILE
            >> Child 1: <expression>
        """
        if len(node.children) == 0:
            return  # No loop condition

        loop_condition_type = node.children[0].value
        expression_node = node.children[1]

        expression_value_nodes = self.get_terminals(expression_node)
        expression_value_node = expression_value_nodes[0]  # Assuming the first terminal node is the value of the expression
        # Check if the expression is of type TROOF (BOTH SAEM, DIFFRINT)
        if expression_value_node.value.type not in [Lexeme.BOTH_SAEM, Lexeme.DIFFRINT]:
            print(f"Error: Loop condition must be a comparison operation. Found '{expression_value_node.value.type}'.")
            return

    # Typecasting
    # <typecast_stmt> ::= varident IS NOW A type
    def visit_typecast_stmt(self, node: Node):
        """
        Visit a typecasting statement node in the parse tree.
            >> Child 0: varident
            >> Child 1: IS NOW A
            >> Child 2: type
        """
        var_ident_node = node.children[0].value
        type_node = node.children[2].value

        # Check if the variable is declared before typecasting
        if not self.symbol_table.exists(var_ident_node.lexeme):
            print(f"Error: Variable '{var_ident_node.lexeme}' is not declared before typecasting.")
            return

        # Update the symbol table with the new type for the variable
        variable_info = self.symbol_table.get(var_ident_node.lexeme)
        self.symbol_table.add(var_ident_node.lexeme, var_ident_node.type, variable_info['value'], type_node.lexeme)
        