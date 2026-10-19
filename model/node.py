from model.token import Token

class Node():
    def __init__(self, value, children=None):
        self.value: Token = value
        self.children: list[Node] = children if children is not None else []

    def display(self, level=0) -> None:
        """
        Recursively prints the parse tree.
        """
        print("  " * level + str(self.value))
        for child in self.children:
            child.display(level + 1)

    def str_children(self) -> str:
        """
        Returns a string representation of the children nodes.
        """
        return "[" + ", ".join(str(child.value) for child in self.children) + "]"

    def __str__(self):
        return f"Node(value={self.value}, children={self.str_children()})"
    
    def __repr__(self):
        return self.__str__()