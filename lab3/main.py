from Machines.NFAMachine import NFA
from Machines.DFAMachine import DFA

# nfa = NFA.from_grammar_file("input.txt")
# nfa.draw_nfa("nfa_output.html")
# print(nfa1, '\n')

nfa = NFA.from_file("input.txt")
nfa.draw_nfa("nfa.html")
print(nfa)

dfa = DFA.from_nfa(nfa)
dfa.draw_dfa("dfa.html")
print(dfa)
