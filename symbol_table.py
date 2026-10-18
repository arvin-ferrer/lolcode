class SymbolTable:
    def __init__(self):
        # Lexeme to { Type, Value, ValueType } mapping
        self.table = {}

    def add(self, lexeme, type, value, value_type,
            parameters=None, return_type=None):
        self.table[lexeme] = {
            "type": type,
            "value": value,
            "value_type": value_type,
            "parameters": parameters,
            "return_type": return_type,
        }

    def get(self, lexeme):
        return self.table.get(lexeme, None)

    def exists(self, lexeme):
        return lexeme in self.table

    def __str__(self):
        return str(self.table)

    def __repr__(self):
        return self.__str__()
    