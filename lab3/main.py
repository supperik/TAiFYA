from NFAMachine import NFA
from DFAMachine import DFA
from Regex import RegexToNFA

nfa1 = NFA.from_grammar_file("input.txt")
nfa1.draw_nfa("nfa_output.html")
print(nfa1, '\n')

# dfa = DFA.from_nfa(nfa1)
# dfa.draw_dfa("dfa_output.html")
# print(dfa)

# regex_converter = RegexToNFA()
# regex = "((ab|aab)*a*)*"
# nfa = regex_converter.regex_to_nfa(regex)
#
# dfa = DFA.from_nfa(nfa)
# # nfa.draw_nfa("output.html")
# # print(nfa.states, nfa.transitions)
# dfa.draw_dfa("output.html")
