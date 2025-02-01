import re
from Token import Token


# определение токенов
tokens = [
    # ключевые слова
    'ARRAY', 'BEGIN', 'ELSE', 'END', 'IF', 'OF', 'OR', 'PROGRAM', 'PROCEDURE', 'THEN', 'TYPE', 'VAR',
    # операторы и знаки пунктуации
    'MULTIPLICATION', 'PLUS', 'MINUS', 'DIVIDE', 'SEMICOLON', 'COMMA', 'LEFT_PAREN', 'RIGHT_PAREN',
    'LEFT_BRACKET', 'RIGHT_BRACKET', 'DOUBLE_EQ', 'EQ', 'GREATER', 'LESS', 'LESS_EQ', 'GREATER_EQ', 'NOT_EQ', 'COLON',
    'ASSIGN', 'DOT',
    # литералы и идентификаторы
    'IDENTIFIER', 'STRING', 'INTEGER', 'FLOAT',
    # комментарии
    'LINE_COMMENT', 'BLOCK_COMMENT',
    # специальные
    'BAD', 'EOF'
]

RESERVED_KEYWORDS = {
    'array': 'ARRAY',
    'begin': 'BEGIN',
    'else': 'ELSE',
    'end': 'END',
    'if': 'IF',
    'of': 'OF',
    'or': 'OR',
    'program': 'PROGRAM',
    'procedure': 'PROCEDURE',
    'then': 'THEN',
    'type': 'TYPE',
    'var': 'VAR',
}

# регулярные выражения для токенов
token_regex = [
    # ключевые слова (регистронезависимые)
    (r'\b(?i:array)\b', 'ARRAY'),
    (r'\b(?i:begin)\b', 'BEGIN'),
    (r'\b(?i:else)\b', 'ELSE'),
    (r'\b(?i:end)\b', 'END'),
    (r'\b(?i:if)\b', 'IF'),
    (r'\b(?i:of)\b', 'OF'),
    (r'\b(?i:or)\b', 'OR'),
    (r'\b(?i:program)\b', 'PROGRAM'),
    (r'\b(?i:procedure)\b', 'PROCEDURE'),
    (r'\b(?i:then)\b', 'THEN'),
    (r'\b(?i:type)\b', 'TYPE'),
    (r'\b(?i:var)\b', 'VAR'),
    (r'\b(?i:float)\b', 'FLOAT'),
    (r'\b(?i:integer)\b', 'INTEGER'),
    (r'\b(?i:boolean)\b', 'BOOLEAN'),
    (r'\b(?i:char)\b', 'CHAR'),

    # комментарии
    (r'//.*', 'LINE_COMMENT'),
    (r'\{[^}]*\}', 'BLOCK_COMMENT'),
    (r'\.\.', 'DOUBLE_DOT'),
    # строка

    (r"'[^']*'", 'STRING'),
    (r"\'[^']*", 'BAD'),

    # Некорректные строки (содержащие кириллицу)
    (r'\b(?:\d+\.)+\d+\.(?:[a-df-zA-DF-Zа-яА-Я]+|[a-df-zA-DF-Zа-яА-Я]+.*)\b', 'BAD'),  # 1.2.3.abc
    (r'\d+[a-zA-Zа-яА-Я]+\d{2,}', 'BAD'),  # "123ff33334bfrf"
    (r'\b\d+[a-df-zA-DF-Zа-яА-Я]+[a-df-zA-DF-Zа-яА-Я0-9_]*\b', 'BAD'),  # "123a123"

    (R"([^\s,.:;(){}\[\]\+\-\*/:=<>]*[а-яА-Я]+[^\s,.:;(){}\[\]\+\-\*/:=<>]*)", "BAD"),  # RUSSIAN

    (r'\b[a-zA-Z_][a-zA-Z0-9_]{256,}\b', 'BAD'),  # identifier > 256 chars

    (r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', 'IDENTIFIER'),

    (r'\d+\.\d+([eE][+-]?\d{3,})', 'BAD'),  # длина > 3
    (r'\.\d+([eE][+-]?(\d{3,}))', 'BAD'),  # длина > 3
    (r'\d+[eE][+-]?\d{3,}', 'BAD'),  # длина > 3
    (r'\d+(?:\.\d+){3,}', 'BAD'),  # длина > 2

    (r'\d+\.\d+([eE][+-]?\d+)?', 'FLOAT'),
    (r'\.\d+([eE][+-]?\d+)?', 'FLOAT'),  # числа, начинающиеся с точки
    (r'\d+[eE][+-]?\d+', 'FLOAT'),  # числа с экспонентой

    (r'-?32768', 'BAD'),  # +-32768
    (r'-?\d{6,}', 'BAD'),  # < 6

    (r'-?\d{1,5}', 'INTEGER'),
    # для интов E, через е больше 1 не воспринимает

    # операторы и пунктуация
    (r':=', 'ASSIGN'),
    (r':', 'COLON'),
    (r'\.', 'DOT'),
    (r'\*', 'MULTIPLICATION'),
    (r'\+', 'PLUS'),
    (r'-', 'MINUS'),
    (r'/', 'DIVIDE'),
    (r';', 'SEMICOLON'),
    (r',', 'COMMA'),
    (r'\(', 'LEFT_PAREN'),
    (r'\)', 'RIGHT_PAREN'),
    (r'\[', 'LEFT_BRACKET'),
    (r'\]', 'RIGHT_BRACKET'),
    (r'<=', 'LESS_EQ'),
    (r'>=', 'GREATER_EQ'),
    (r'<>', 'NOT_EQ'),
    (r'==', 'DOUBLE_EQ'),
    (r'=', 'EQ'),
    (r'>', 'GREATER'),
    (r'<', 'LESS'),
    # при пустом токен выводить пустого

    # пробелы и конец строки
    (r'[ \t]+', None),
    (r'\n', None),

    # некорректные символы
    (r'\{[^}]*', 'BAD'),
    (r'[^\s]', 'BAD'),
    (r'\n', 'BAD'),
]


class PascalLexer:
    def __init__(self, input_file):
        self.input_file = input_file
        self.tokens = []
        self.current_line = 1
        self.current_column = 1
        self.buffer = ""
        self.position = 0

    def next_token(self):
        if self.position >= len(self.buffer):
            return

        for regex, token_type in token_regex:
            match = re.match(regex, self.buffer[self.position:])

            if match:
                lexeme = match.group(0)
                # print(regex, lexeme)

                if token_type is None:
                    if '\n' in lexeme:
                        self.current_line += lexeme.count('\n')
                        self.current_column = 1
                    else:
                        self.current_column += len(lexeme)
                    self.position += len(lexeme)
                    return self.next_token()

                token = Token(token_type, lexeme, self.current_line, self.current_column)
                self.position += len(lexeme)
                self.current_column += len(lexeme)
                # print(token)

                if token_type == 'BLOCK_COMMENT':
                    newline_count = lexeme.count('\n')
                    self.current_line += newline_count
                    return self.next_token()
                if token_type == 'LINE_COMMENT':
                    return self.next_token()
                if token_type == 'IDENTIFIER' and lexeme.lower() in RESERVED_KEYWORDS:
                    return Token('BAD', lexeme, self.current_line, self.current_column)
                return token

        # если не удалось распознать токен, возвращаем BAD
        lexeme = self.buffer[self.position]
        token = Token('BAD', lexeme, self.current_line, self.current_column)

        self.position += 1
        self.current_column += 1
        return token

    def tokenize(self, output_file):
        with open(self.input_file, 'r', encoding='utf-8') as file:
            self.buffer = file.read()

            if not self.buffer.strip():
                return [Token('BAD', 'Empty File', 1, 1)]

        tokens = []
        while True:
            token = self.next_token()
            if token is None:
                break
            tokens.append(token)
        return tokens
