import sys
from Lexer import PascalLexer


input_file = "test.pas"
output_file = "output.txt"

lexer = PascalLexer(input_file)
tokens = lexer.tokenize(output_file)

with open(output_file, 'w', encoding='utf-8') as output:
    for token in tokens:
        print(token)
        output.write(str(token) + '\n')
