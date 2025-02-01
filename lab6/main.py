import re

# Ключевые слова Паскаля
KEYWORDS = {"begin", "end", "program", "var", "integer", "char", "boolean", "if", "else", "array", "of", "then",
            "float"}

# Символы и операторы
TOKENS = {
    ':=': "ASSIGNMENT",
    '<>': "NOT_EQUAL",
    '<': "LESS_THAN",
    '>': "GREATER_THAN",
    '=': "EQUALS",
    ':': "COLON",
    ';': "SEMICOLON",
    '.': "DOT",
    ',': "COMMA",
    '(': "LEFT_PAREN",
    ')': "RIGHT_PAREN",
    '+': "PLUS",
    '-': "MINUS",
    '*': "MULTIPLY",
    '/': "DIVIDE",
    '[': "LEFT_BRACKET",
    ']': "RIGHT_BRACKET"
}


class Lexer:
    def __init__(self, code):
        self.code = code
        self.pos = 0
        self.line = 1
        self.column = 1

    def next_char(self):
        if self.pos < len(self.code):
            ch = self.code[self.pos]
            self.pos += 1
            if ch == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            return ch
        return None

    def peek(self):
        return self.code[self.pos] if self.pos < len(self.code) else None

    def tokenize(self):
        tokens = []
        if len(self.code) == 0:
            tokens.append(("BAD", self.line, self.column, "Файл пустой"))
        while self.pos < len(self.code):
            ch = self.next_char()

            if ch.isspace():
                continue
            try:
                if ch == '/' and self.peek() == '/':  # Однострочный комментарий
                    while self.peek() and self.peek() != '\n':
                        self.next_char()
                    continue

                if ch == '{':  # Блочный комментарий
                    start_col = self.column - 1
                    while self.peek() and self.peek() != '}':
                        self.next_char()
                    if not self.peek():
                        tokens.append(("BAD", self.line, start_col, "Незакрытый блочный комментарий"))
                    else:
                        self.next_char()
                    continue

                if ch.isalpha() or ch == '_':  # Идентификатор или ключевое слово
                    start_col = self.column - 1
                    identifier = ch
                    while self.peek() and (self.peek().isalnum() or self.peek() == '_'):
                        identifier += self.next_char()

                    if len(identifier) > 256 or re.search(r'[^a-zA-Z0-9_]', identifier):
                        tokens.append(("BAD", self.line, start_col, identifier))
                        continue

                    token_type = identifier.upper() if identifier.lower() in KEYWORDS else "IDENTIFIER"
                    tokens.append((token_type, self.line, start_col, identifier))

                elif ch.isdigit() or (
                        ch == '.' and self.peek() and self.peek().isdigit()):  # Число (целое или с точкой)

                    start_col = self.column - 1
                    number = ch
                    is_float = False
                    is_double = False
                    bad_float_token = False

                    while self.peek() and self.peek().isdigit():
                        number += self.next_char()

                    if self.peek() == '.':  # Дробное число или просто точка
                        number += self.next_char()

                        if self.peek() == '.':
                            tokens.append(("NUMBER", self.line, start_col, number[0:-1]))
                            tokens.append(("DOT", self.line, start_col, '.'))
                            self.next_char()
                            tokens.append(("DOT", self.line, self.column, '.'))
                            continue

                        while self.peek() and self.peek().isdigit():
                            number += self.next_char()
                            if self.peek() == '.':
                                number += self.next_char()
                                bad_float_token = True

                        if bad_float_token:
                            tokens.append(("BAD", self.line, start_col, number))
                            continue

                    is_double = '.' in number

                    if self.peek() and self.peek().lower() == 'e':  # Экспоненциальная запись
                        number += self.next_char()

                        if self.peek() in ['+', '-']:
                            number += self.next_char()

                        if not self.peek().isdigit():
                            tokens.append(("BAD", self.line, start_col, number))
                            continue

                        while self.peek() and self.peek().isdigit():
                            number += self.next_char()

                        if '+' in number.split('e')[-1] or '-' in number.split('e')[-1]:
                            if len(number.split('e')[-1][1:]) > 2:
                                tokens.append(("BAD", self.line, start_col, number))
                                continue
                            is_float = True
                        else:
                            if len(number.split('e')[-1]) > 2:
                                tokens.append(("BAD", self.line, start_col, number))
                                continue
                            is_float = True

                    try:
                        if int(number) >= 32256:
                            tokens.append(("BAD", self.line, start_col, number))
                            continue
                    except Exception as e:
                        pass

                    if self.peek() and self.peek().isalpha():  # Число с буквами (ошибка)
                        while self.peek() and self.peek().isalnum():
                            number += self.next_char()
                        tokens.append(("BAD", self.line, start_col, number))
                    else:
                        token_type = "FLOAT_NUMBER" if is_float else "DOUBLE_NUMBER" if is_double else "INTEGER_NUMBER"
                        tokens.append((token_type, self.line, start_col, number))

                elif ch in TOKENS or (ch + (self.peek() or '')) in TOKENS:  # Операторы и символы
                    start_col = self.column - 1
                    two_char_token = ch + (self.peek() or '')
                    if two_char_token in TOKENS:
                        self.next_char()
                        tokens.append((TOKENS[two_char_token], self.line, start_col, two_char_token))
                    else:
                        tokens.append((TOKENS[ch], self.line, start_col, ch))

                elif ch == "'" or ch == '"':  # Строка
                    start_col = self.column - 1
                    start_line = self.line
                    string_lit = "'"
                    while self.peek() and self.peek() != "'":
                        string_lit += self.next_char()
                    if not self.peek():
                        tokens.append(("BAD", start_line, start_col, f"Незакрытая строка: {string_lit}"))
                        # self.column = 0
                        # self.line = start_line + 1
                        # self.pos = start_pos + end_line_pos + 1
                        continue
                    else:
                        string_lit += self.next_char()
                        tokens.append(("STRING_TEXT", start_line, start_col, string_lit))

                else:
                    tokens.append(("BAD", self.line, self.column - 1, f"Неизвестный символ: {ch}"))
            except Exception as e:
                tokens.append(("BAD", self.line, self.column - 1, str(e)))
        return tokens


# Чтение кода из файла
with open("test.pas", "r", encoding="utf-8") as file:
    code = file.read()

lexer = Lexer(code)
tokens = lexer.tokenize()
with open("output.txt", "w", encoding="utf-8") as out_file:
    for token in tokens:
        out_file.write(f"{token[0]}({token[1]}, {token[2]})-\"{token[3]}\"\n")
        print(f"{token[0]}({token[1]}, {token[2]})-\"{token[3]}\"")
