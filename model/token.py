
class Token():
    def __init__(self, lexeme, type):
        self.lexeme = lexeme     # Type of the token
        self.type = type          # Value of the token
    def __str__(self):
        return f"Token(lexeme={self.lexeme.replace('\n', '\\n').replace('\t', '\\t').replace('\r', '\\r')}, type={self.type})"
    def __repr__(self):
        return self.__str__()