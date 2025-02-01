from RegexToNfa import RegexToNFA

regex = "((a*c+b*)|(b*a+c*)|(c*b+a*))"
parser = RegexToNFA(regex)
nfa = parser.parse_regex()
table = parser.nfa_to_table(nfa)

print(table)
