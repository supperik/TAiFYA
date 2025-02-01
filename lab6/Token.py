# класс для хранения информации о токене
class Token:
    def __init__(self, type, lexeme, line, column):
        self.type = type
        self.lexeme = lexeme
        self.line = line
        self.column = column

    def __str__(self):
        return f'{self.type} ({self.line}, {self.column}) "{self.lexeme}"'