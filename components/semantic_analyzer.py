import math
import re
import sys

from model.lexeme import Lexeme
from model.token import Token
from model.node import Node
from model.symbol_table import SymbolTable
from model.frame import Frame

class SemanticAnalyzer:
    """
    Executes a parse tree using recursive descent tree-walking.
    """
    def __init__(self, output_fn=None, input_fn=None, strict_noob_to_yarn: bool = False):
        if output_fn is None or output_fn is print:
            self.output_fn = lambda text: print(text, end="")
        else:
            self.output_fn = output_fn
        self.input_fn = input_fn if input_fn else input

        self.symbol_table: SymbolTable = None
        self.function_table: SymbolTable = None
        self.function_bodies: dict[str, Node] = {}
        self.frame: Frame = None

        # Parameter to control strict NOOB to YARN casting
        self.STRICT_NOOB_TO_YARN = strict_noob_to_yarn

    def run(self, parse_tree: Node) -> SymbolTable:
        """
        Run the semantic analyzer on the given parse tree and return the symbol table.
        """
        # Increase recursion limit to handle deep parse trees
        sys.setrecursionlimit(max(sys.getrecursionlimit(), 10000))

        # Initialize the symbol table, function table, and frame for execution
        self.symbol_table = SymbolTable()
        self.function_table = SymbolTable()
        self.function_bodies = {}
        self.frame = Frame(self.symbol_table)

        children = parse_tree.children      # Get the children of the root node (program structure)
        try:
            # Register functions from the program's function definitions
            self.register_functions(children[0])
            self.register_functions(children[6])

            for decl in self.collect(children[3], "declaration"):
                # Guard with try-except to catch recursion errors and provide context
                # Execute declaration
                self.guard(decl, self.exec_declaration, decl)
            self.exec_block(children[4])    # Execute the main program block
        except RecursionError:
            raise RuntimeError("Semantic error: Maximum recursion depth exceeded (runaway recursive function?)")
        return self.symbol_table

    @staticmethod
    def collect(node: Node, name: str) -> list[Node]:
        """
        Collect all nodes with the given name in the subtree rooted at the given node.
        """
        found, stack = [], [node]
        while stack:
            n = stack.pop()
            if n.value == name:
                found.append(n)
            else:
                stack.extend(reversed(n.children))
        return found

    @staticmethod
    def flatten_statements(node: Node) -> list[Node]:
        """
        Get statements from a subtree, then return the list of statements in order.
        """
        statements = []             # List to hold the collected statements
        while node is not None:
            nxt = None              # Variable to hold the next statement_list node if it exists
            for child in node.children:         
                if child.value == "statement":
                    statements.append(child)    # If statement node, add to statements
                elif child.value == "statement_list":
                    nxt = child                 # If statement_list node, set nxt to it for further traversal
            node = nxt                          # Move to the next statement_list node for further traversal
        return statements

    @staticmethod
    def flatten_expr_list(node: Node) -> list[Node]:
        """
        Get expressions from a subtree, then return the list of expressions in order.
        """
        out = []                        # List to hold the collected expressions
        while node is not None:
            nxt = None                  # Variable to hold the next expr_list node if it exists
            for child in node.children:
                if child.value == "expression":
                    out.append(child)   # If expression node, add to out
                elif child.value == "expr_list":
                    nxt = child         # If expr_list node, set nxt to it for further traversal
            node = nxt
        return out

    @staticmethod
    def source_text(node: Node) -> str:
        """
        Get the source text corresponding to a node in the parse tree, up to 12 tokens or until a newline is encountered.
        """
        # Track the tokens and nodes to reconstruct the source text
        # Out is the list of lexemes to return
        # Stack is used for depth-first traversal of the parse tree
        out, stack = [], [node]
        while stack and len(out) < 12:
            n = stack.pop()                 # Pop the last node from the stack for processing
            if isinstance(n.value, Token):  # If the node's value is a Token, process it
                if n.value.type == Lexeme.NEWLINE:
                    break                   # Stop processing if a newline token is encountered
                out.append(n.value.lexeme)
            else:                           # Add the children of the node to the stack for further processing
                stack.extend(reversed(n.children))
        return " ".join(out)

    def guard(self, node: Node, fn, *args):
        """
        Surround a function with a try-except block to catch runtime errors
        """
        try:
            # Return the result of the function call with the provided arguments
            return fn(*args)
        except RuntimeError as e:
            if "[near:" not in str(e):
                raise RuntimeError(f"{str(e)}  [near: {self.source_text(node)}]")
            raise

    @staticmethod
    def literal_type(value) -> Lexeme:
        """
        Determine the type of a literal value.
        """
        if value is None: 
            return Lexeme.NOOB_LITERAL
        if isinstance(value, bool): 
            return Lexeme.TROOF_LITERAL
        if isinstance(value, int): 
            return Lexeme.NUMBR_LITERAL
        if isinstance(value, float): 
            return Lexeme.NUMBAR_LITERAL
        return Lexeme.YARN_LITERAL

    def set_var(self, name: str, value) -> None:
        """
        Set the value of a variable in the current frame's symbol table.
        """
        self.frame.table.add(name, Lexeme.VARIABLE_IDENTIFIER, value, self.literal_type(value))

    def get_var(self, name: str):
        """
        Get the value of a variable from the current frame's symbol table.
        Raises an error if the variable is not declared.
        """
        entry = self.frame.table.get(name)
        if entry is None:
            raise RuntimeError(f"Semantic error: Variable '{name}' is not declared")
        return entry["value"]

    def set_it(self, value) -> None:
        """
        Set the implicit IT variable in the current frame's symbol table.
        """
        self.set_var("IT", value)

    @staticmethod
    def literal_value(token: Token):
        """
        Get the literal value of a token based on its type.
        """
        s = token.lexeme
        if token.type == Lexeme.NUMBR_LITERAL: 
            return int(s)
        if token.type == Lexeme.NUMBAR_LITERAL: 
            return float(s)
        if token.type == Lexeme.YARN_LITERAL: 
            return s[1:-1]
        return s == "WIN"

    @staticmethod
    def to_troof(value) -> bool:
        """
        Convert a value to a boolean (TROOF).
        """
        if value is None:           # NOOB is considered false in boolean context
            return False
        if isinstance(value, bool): # Return the boolean value directly
            return value
        if isinstance(value, (int, float)): 
            return value != 0       # Cast 
        return value != ""

    @staticmethod
    def to_number(value, explicit: bool = False):
        """
        Convert a value to a number (NUMBR or NUMBAR).
        Raises an error if the conversion is not possible and explicit is False.
        """
        if value is None:   # NOOB cannot be implicitly cast to a number
            if explicit:    # If explicit is True, return 0 for NOOB
                return 0
            raise RuntimeError("Semantic error: A NOOB cannot be implicitly cast to a number")
        if isinstance(value, bool):         # If bool, return 1 for True and 0 for False
            return 1 if value else 0
        if isinstance(value, (int, float)): # If number, return it directly
            return value
        # Strip whitespaces before converting string numbers
        value = value.strip() if isinstance(value, str) else str(value)
        # Case where it is a YARN
        # Cast into int or float if possible, otherwise raise an error
        if re.fullmatch(r"-?\d+", value):   # If integer, cast it to int
            return int(value)
        if re.fullmatch(r"-?(\d+\.\d*|\.\d+)", value): 
            return float(value)             # If float, cast it to float
        raise RuntimeError(f"Semantic error: Cannot cast YARN \"{value}\" to a number")

    def to_yarn(self, value, explicit: bool = False) -> str:
        """
        Convert a value to a YARN (string).
        Raises an error if the conversion is not possible and explicit is False.
        """
        if value is None:   # NOOB cannot be implicitly cast to a YARN
            if explicit or not self.STRICT_NOOB_TO_YARN: 
                return ""   # If explicit is True or strict casting is disabled, return an empty string for NOOB
            raise RuntimeError("Semantic error: A NOOB cannot be implicitly cast to a YARN")
        if isinstance(value, bool):     # If boolean, return "WIN" for True and "FAIL" for False
            return "WIN" if value else "FAIL"
        if isinstance(value, int):      # If integer, return its string representation
            return str(value)
        if isinstance(value, float):    # If float, format it to a string with up to 2 decimal places, avoiding scientific notation
            s = repr(round(value, 10)) if math.isfinite(value) else repr(value)           
            if "e" in s or "inf" in s or "nan" in s: s = f"{value:f}"
            whole, _, frac = s.partition(".")
            return f"{whole}.{frac[:2]}" if frac else whole
        return value

    def cast(self, value, target: str):
        """
        Cast a value to a target type.
        """
        if target == "NOOB": 
            return None
        if target == "TROOF": 
            return self.to_troof(value)
        if target == "NUMBR": 
            return int(self.to_number(value, explicit=True))
        if target == "NUMBAR": 
            return float(self.to_number(value, explicit=True))
        if target == "YARN": 
            return self.to_yarn(value, explicit=True)
        raise RuntimeError(f"Semantic error: Unknown type '{target}'")

    @staticmethod
    def get_kind(value) -> str:
        """
        Get the kind of a value as a string representation of its type.
        """
        if value is None: 
            return "NOOB"
        if isinstance(value, bool): 
            return "TROOF"
        if isinstance(value, (int, float)): 
            return "NUM"
        return "YARN"

    @classmethod
    def values_equal(cls, a, b) -> bool:
        """
        Check if two values are equal, considering their types.
        """
        return cls.get_kind(a) == cls.get_kind(b) and a == b

    def register_functions(self, outer_blocks: Node) -> None:
        """
        Register all function definitions found in the given outer blocks into the function table.
        """
        # Iterate through all function definition nodes in the outer blocks
        for func_def_node in self.collect(outer_blocks, "func_def"):
            name = func_def_node.children[1].value.lexeme   # Get name
            if self.function_table.exists(name):            # If already defined in the symbol table, raise an error
                raise RuntimeError(f"Semantic error: Function '{name}' is already defined")
            params, body = [], None                         # Params and body of the function
            for child in func_def_node.children:            # Iterate the childrens
                if child.value == "func_params":            # If func_params, collect the parameter names
                    node = child
                    while node is not None:                 # Iterate through the func_params node to collect parameter names
                        param_name = node.children[1].value.lexeme
                        if param_name in params:            # If already in params, raise an error for duplicate parameter
                            raise RuntimeError(f"Semantic error: Duplicate parameter '{param_name}' in function '{name}'")
                        params.append(param_name)           # Add the parameter name to the params list
                        node = node.children[3] if len(node.children) > 3 else None
                elif child.value == "statement_list":       # If statement_list, this is the body of the function
                    body = child
            # Add the function to the function table with its parameters and body
            self.function_table.add(name, Lexeme.FUNCTION_IDENTIFIER, None, None,
                                    parameters=params, return_type=None)
            self.function_bodies[name] = body

    def call_function(self, name: str, args: list):
        """
        Call the function with the given name and arguments, executing its body in a new frame.
        """
        # Retrieve the function information from the function table 
        info = self.function_table.get(name)
        # Handle missing function definition or incorrect number of arguments
        if info is None:
            raise RuntimeError(f"Semantic error: Function '{name}' is not defined")
        params = info["parameters"]
        if len(args) != len(params):
            raise RuntimeError(f"Semantic error: Function '{name}' expects {len(params)} argument(s), got {len(args)}")

        # Create a new frame for the function call, passing the arguments to the parameters
        callee = Frame(in_function=True)
        # Add params to the frame
        for param_name, value in zip(params, args):
            callee.table.add(param_name, Lexeme.VARIABLE_IDENTIFIER, value, self.literal_type(value))

        # Switch the current frame to the callee frame
        caller, self.frame = self.frame, callee
        result = None
        
        # Execute the function body and handle control flow signals (RETURN, BREAK)
        signal = self.exec_block(self.function_bodies[name])

        # Handle the result if RETURN or BREAK
        if isinstance(signal, tuple) and signal[0] == "RETURN":
            result = signal[1]
        elif signal == "BREAK":
            result = None

        self.frame = caller                                 # Restore the frame to the caller's frame
        info["return_type"] = self.literal_type(result)     # Update the return type of the function in the function table based on the result
        self.set_it(result)                                 # Set the implicit IT variable to the result of the function call
        return result

    def exec_block(self, statement_list: Node):
        """
        Execute a list of statements and return the first control flow signal encountered.
        """
        for stmt in self.flatten_statements(statement_list):
            # Returns the signal from the executed statement
            signal = self.exec_statement(stmt)
            if signal is not None:
                return signal
        # Return None if there is no statement or no signal
        return None

    def exec_statement(self, node: Node):
        """
        Execute a single statement
        """
        child = node.children[0]
        # Guard the execution of the statement with error handling and return the result
        return self.guard(node, self.dispatch_statement, child)

    def dispatch_statement(self, child: Node):
        """
        Call the appropriate execution method based on the type of statement.
        """
        if isinstance(child.value, Token):
            if self.frame.break_depth == 0:     # If GTFO is used outside of a loop, switch-case, or function, raise an error
                raise RuntimeError("Semantic error: GTFO used outside of a loop, switch-case or function")
            return "BREAK"                      # Return "BREAK" signal to indicate a break in the current loop or switch-case
        # If the child is not a Token, call the corresponding execution method based on the statement type
        return getattr(self, f"exec_{child.value}")(child)

    # Execution methods for different statement types

    # No operation for comments and multi-line comments
    def exec_inline_comment(self, node): pass
    def exec_multi_comment(self, node): pass

    def exec_expression(self, node: Node):
        """
        Evaluate an expression and set the implicit IT variable to its value.
        """
        self.set_it(self.eval_expression(node))

    def exec_declaration(self, node: Node):
        """
        Execute a variable declaration statement
        """
        name = node.children[1].value.lexeme    # Get the variable name
        if self.frame.table.exists(name):       # If it exists in symbol table, raise an error
            raise RuntimeError(f"Semantic error: Variable '{name}' is already declared")
        # Evaluate expression and get the value
        value = self.eval_expression(node.children[3]) if len(node.children) > 2 else None
        # Set the value to the variable in the current frame's symbol table
        self.set_var(name, value)

    def exec_assignment(self, node: Node):
        """
        Execute a variable assignment statement
        """
        name = node.children[0].value.lexeme    # Get the variable name
        if not self.frame.table.exists(name):   # If it does not exist in the symbol table, raise an error
            raise RuntimeError(f"Semantic error: Variable '{name}' is not declared before assignment")
        # Update the variable's value in the current frame's symbol table with the evaluated expression
        self.set_var(name, self.eval_expression(node.children[2]))

    def exec_input(self, node: Node):
        """
        Execute an input statement, reading a value from the user and assigning it to a variable.
        """
        name = node.children[1].value.lexeme    # Get the variable name
        if not self.frame.table.exists(name):   # If it does not exist in the symbol table, raise an error
            raise RuntimeError(f"Semantic error: Variable '{name}' is not declared before GIMMEH")
        text = self.input_fn()                  # Get the input from the user
        # Update the variable's value in the current frame's symbol table with the input value
        self.set_var(name, "" if text is None else str(text))

    def exec_print(self, node: Node):
        """
        Execute a print statement, evaluating expressions and printing their values as a concatenated string.
        """
        # Evaluate the expressions in the print statement
        parts, pl = [], node.children[1]
        while pl is not None:       # Walk through the expr_list nodes
            # Evaluate the expression then append the parsed yarn to the parts list
            parts.append(self.to_yarn(self.eval_expression(pl.children[0])))
            # Iterate if there is more to the expr_list
            pl = pl.children[2] if len(pl.children) > 2 else None
        # Print the concatenated string to the output function
        self.output_fn("".join(parts) + "\n")

    def exec_typecast_stmt(self, node: Node):
        """
        Execute a typecast statement, converting a variable to a different type.
        """
        name = node.children[0].value.lexeme                # Get the variable name
        target = node.children[2].children[0].value.lexeme  # Get the target type to cast to
        # Set the variable to the casted value in the current frame's symbol table
        self.set_var(name, self.cast(self.get_var(name), target))

    def exec_return_stmt(self, node: Node):
        """
        Execute a return statement, returning a value from a function.
        """
        if not self.frame.in_function:  # If the return statement is used outside of a function, raise an error
            raise RuntimeError("Semantic error: FOUND YR used outside of a function")
        # Return a tuple with the signal "RETURN" and the evaluated expression value
        return ("RETURN", self.eval_expression(node.children[1]))

    def exec_conditional(self, node: Node):
        """
        Execute a conditional statement
        """
        children = node.children                # Get the children of the conditional node
        if self.to_troof(self.get_var("IT")):   # Return the result of the first block if IT is true
            return self.exec_block(children[4]) 
        
        mebbe = children[5]                     # Get first meebe block
        # Walk through the meebe blocks, 
        # evaluating the conditions and executing the corresponding block if a condition is true
        while mebbe is not None and mebbe.children:
            # Evaluate the meebe block and return if true
            if self.to_troof(self.eval_expression(mebbe.children[1])):
                return self.exec_block(mebbe.children[3])
            # Continue to next if false
            mebbe = mebbe.children[4] if len(mebbe.children) > 4 else None

        # If there is an else block, execute it if all conditions are false
        if children[6].children:
            return self.exec_block(children[6].children[2])

    def exec_switch(self, node: Node):
        """
        Execute a switch-case statement, evaluating the cases and executing the corresponding block.
        """
        children = node.children        # Get the children of the switch node
        it = self.get_var("IT")         # Get the value of the implicit IT variable to compare against the case values

        cases, case = [], children[2]   # Get the list of cases and the first case node
        # Build the list of cases and their corresponding blocks
        while case is not None and case.children:
            # Append a tuple of the case literal value and the corresponding block to the cases list
            cases.append((self.literal_value(case.children[1].children[0].value), case.children[3]))
            case = case.children[4] if len(case.children) > 4 else None # Move to the next case node if it exists
        
        # Build the list of blocks to execute, including the default block if it exists
        blocks = [body for _, body in cases]
        default = children[3].children[2] if children[3].children else None
        # Add the default block to the list of blocks if it exists
        if default is not None:
            blocks.append(default)

        # Find the index of the first case that matches the value of IT, 
        # Use the default block if no match is found
        start = None
        for i, (lit, _) in enumerate(cases):
            if self.values_equal(it, lit):
                start = i
                break
        # If no matching case is found, start from the default block if it exists
        if start is None:
            if default is None:
                return
            start = len(cases)

        # Add 1 to the break depth to allow GTFO inside the switch-case block
        self.frame.break_depth += 1
        signal = None
        # Walk through the cases and default block
        for body in blocks[start:]:
            signal = self.exec_block(body)
            # Handle control flow signals (BREAK, RETURN) and exit the switch-case block accordingly
            if signal == "BREAK":
                signal = None 
                break
            if signal is not None: 
                break
        # Decrease the break depth after exiting the switch-case block
        self.frame.break_depth -= 1
        return signal

    def exec_loop(self, node: Node):
        """
        Execute a loop statement, iterating based on the loop condition and executing the loop body.
        """
        children = node.children        # Get the children of the loop node
        frame = self.frame              # Get the current frame for scoping

        label, end_label = children[1].value.lexeme, children[10].value.lexeme  # Get the label and end label of the loop
        action = children[2].children[0].value.type                             # Get the action
        var = children[4].value.lexeme                                          # Get the loop variable
        cond, body = children[5], children[7]                                   # Get the condition and body of the loop

        if label != end_label:          # Make sure that the loop label and end label match
            raise RuntimeError(f"Semantic error: Loop label '{end_label}' does not match '{label}'")
        if label in frame.loop_labels:  # Make sure that the loop label is not already used by an enclosing loop
            raise RuntimeError(f"Semantic error: Loop label '{label}' is already used by an enclosing loop")
        if not frame.table.exists(var): # Var must be declared
            raise RuntimeError(f"Semantic error: Loop variable '{var}' is not declared")

        # Add loop label to the frame
        frame.loop_labels.append(label)
        # Increase the break depth to allow GTFO inside the loop
        frame.break_depth += 1
        signal = None

        # Execute the loop until the condition is met or a control flow signal is encountered
        while True:
            if cond.children:   # If there is a condition, evaluate it and check if the loop should continue
                keep = self.to_troof(self.eval_expression(cond.children[1]))
                if cond.children[0].value.type == Lexeme.TIL and keep: break
                if cond.children[0].value.type == Lexeme.WILE and not keep: break

            # Execute the loop body and check for control flow signals (BREAK, RETURN)
            signal = self.exec_block(body)

            # Handle control flow signals
            if signal == "BREAK":
                signal = None 
                break
            if signal is not None:
                break
            
            # Update the loop variable based on the action (UPPIN or NERFIN)
            current = self.to_number(self.get_var(var))
            # Increment or decrement the loop variable based on the action type
            self.set_var(var, current + 1 if action == Lexeme.UPPIN else current - 1)

        # Cleanup after the loop execution
        # Remove the loop label and decrease the break depth
        frame.break_depth -= 1
        frame.loop_labels.pop()
        return signal

    def eval_expression(self, node: Node):
        """
        Execute an expression node and return its evaluated value.
        """
        inner = node.children[0]        # Get the first child of the expression node
        # Call the appropriate evaluation method based on the type of expression
        return getattr(self, f"eval_{inner.value}")(inner)

    def eval_operand(self, node: Node):
        """
        Execute an operand node, which can be a variable or a literal, and return its value.
        """
        child = node.children[0]            # Get the first child of the operand node
        if isinstance(child.value, Token):  # If the child is a Token, it is a variable, so return its value
            return self.get_var(child.value.lexeme)
        # If the child is not a Token, it is a literal, so return its literal value
        return self.literal_value(child.children[0].value)

    def eval_arithmetic_expr(self, node: Node):
        """
        Execute an arithmetic expression node, performing the specified operation on its operands and returning the result.
        """
        children = node.children        # Get children of the arithmetic expression node
        op = children[0].value.type     # Get operations
        # Get the evaluated values of the operands and convert them to numbers
        x = self.to_number(self.eval_expression(children[1]))
        y = self.to_number(self.eval_expression(children[3]))

        # Check if both operands are integers for certain operations
        both_int = isinstance(x, int) and isinstance(y, int)

        # Calculate the result based on the operation type
        if op == Lexeme.SUM_OF: 
            return x + y
        if op == Lexeme.DIFF_OF: 
            return x - y
        if op == Lexeme.PRODUKT_OF:
            return x * y
        if op in (Lexeme.QUOSHUNT_OF, Lexeme.MOD_OF):
            # Handle division by zero error for QUOSHUNT_OF and MOD_OF operations
            if y == 0: raise RuntimeError("Semantic error: Division by zero")
            if op == Lexeme.QUOSHUNT_OF:
                # Divide x and y using trunc_div for int division
                return self.trunc_div(x, y) if both_int else x / y
            # Calculate for the modulo operation
            return x - y * self.trunc_div(x, y) if both_int else math.fmod(x, y)

        # Handle BIGGR_OF and SMALLR_OF operations, returning the maximum or minimum of the two operands
        result = max(x, y) if op == Lexeme.BIGGR_OF else min(x, y)
        return result if both_int else float(result)

    @staticmethod
    def trunc_div(x: int, y: int) -> int:
        """
        Execute truncating division of two integers, returning the quotient rounded towards zero.
        """
        # Calculate for abs division of two variables
        q = abs(x) // abs(y)
        # Return the quotient rounded towards zero, adjusting the sign based on the signs of x and y
        return -q if (x < 0) != (y < 0) else q

    def eval_boolean_expr(self, node: Node):
        """
        Execute a boolean expression node.
        Perform the specified logical operation on its operands and returning the result.
        """
        children = node.children            # Get the children of the boolean expression node
        op = children[0].value.type         # Get the operator type of the boolean expression
        if op == Lexeme.NOT:                        # Evaluate NOT op
            return not self.to_troof(self.eval_expression(children[1]))
        if op in (Lexeme.ALL_OF, Lexeme.ANY_OF):    # Evaluate ALL OF or ANY OF op
            values = [self.to_troof(self.eval_expression(e)) for e in self.flatten_expr_list(children[1])]
            return all(values) if op == Lexeme.ALL_OF else any(values)
        
        # Evaluate BOTH OF, EITHER OF, or DIFFRINT OF op
        a = self.to_troof(self.eval_expression(children[1]))    # Evaluate the first operand and convert it to a boolean (TROOF)
        b = self.to_troof(self.eval_expression(children[3]))    # Evaluate the second operand and convert it to a boolean (TROOF)
        if op == Lexeme.BOTH_OF: return a and b     # Evaluate BOTH OF expression
        if op == Lexeme.EITHER_OF: return a or b    # Evaluate EITHER OF expression
        return a != b   # Evaluate IS DIFFRINT expression 

    def eval_comparison_expr(self, node: Node):
        """
        Evaluate a comparison expression node, checking for equality or inequality between its operands and returning the result.
        """
        children = node.children        # Get the children of the comparison expression node
        # Check if the values of the two operands are equal using the values_equal method
        equal = self.values_equal(self.eval_expression(children[1]), self.eval_expression(children[3]))
        return equal if children[0].value.type == Lexeme.BOTH_SAEM else not equal

    def eval_concatenation_expr(self, node: Node):
        """
        Evaluate a concatenation expression node, joining the string representations of its operands and returning the result.
        """
        # Concatenate the string expressions
        return "".join(self.to_yarn(self.eval_expression(e))
                       for e in self.flatten_expr_list(node.children[1]))

    def eval_typecast_expr(self, node: Node):
        """
        Evaluate a typecast expression node, converting the value of an expression to a specified target type and returning the result.
        """
        children = node.children                        # Get the children of the typecast expression node
        target = children[-1].children[0].value.lexeme  # Get the target type for the typecast from the last child node
        return self.cast(self.eval_expression(children[1]), target)

    def eval_func_call(self, node: Node):
        """
        Evaluate a function call expression node, executing the function with the provided arguments and returning the result.
        """
        children = node.children            # Get the children of the function call node
        name = children[1].value.lexeme     # Get name
        # Get the list of args and attr_nodes
        args, attr_node = [], children[2] if len(children) == 4 else None
        # Iterate through the attribute nodes to collect the arguments for the function call
        while attr_node is not None:
            args.append(self.eval_expression(attr_node.children[1]))
            attr_node = attr_node.children[3] if len(attr_node.children) > 3 else None
        # Call function with the collected arguments and return the result
        return self.call_function(name, args)