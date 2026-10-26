from model.symbol_table import SymbolTable
from model.lexeme import Lexeme

class Frame:
    """One variable scope. The global program has one; every function call gets its own,
    so a function can never see the caller's (or the program's) variables."""

    def __init__(self, table: SymbolTable | None = None, in_function: bool = False):
        self.table = table if table is not None else SymbolTable()
        self.table.add("IT", Lexeme.VARIABLE_IDENTIFIER, None, Lexeme.NOOB_LITERAL)  # implicit IT
        self.in_function = in_function
        self.break_depth = 1 if in_function else 0   # GTFO inside a function returns NOOB
        self.loop_labels = []                        # labels of the loops currently running

