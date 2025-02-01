from State import State
from NFAMachine import NFA


class RegexToNFA:
    def __init__(self, regex):
        self.regex = regex

    def parse_regex(self):
        postfix = self.infix_to_postfix(self.regex)
        return self.postfix_to_nfa(postfix)

    def infix_to_postfix(self, regex):
        precedence = {"|": 1, ".": 2, "*": 3, "+": 3, "(": 0}
        output = []
        operators = []

        def add_concatenation_symbols(regex):
            result = []
            for i, char in enumerate(regex):
                result.append(char)
                if i + 1 < len(regex):
                    if (char.isalnum() or char == ')' or char in '*+') and (
                            regex[i + 1].isalnum() or regex[i + 1] == '('):
                        result.append('.')
            return ''.join(result)

        regex = add_concatenation_symbols(regex)

        for char in regex:
            if char == '(':
                operators.append(char)
            elif char == ')':
                while operators and operators[-1] != '(':
                    output.append(operators.pop())
                if not operators:
                    raise ValueError("Несоответствие скобок в выражении.")
                operators.pop()
            elif char in ['|', '.', '*', '+']:
                while (operators and
                       precedence[operators[-1]] >= precedence[char]):
                    output.append(operators.pop())
                operators.append(char)
            else:
                output.append(char)

        while operators:
            if operators[-1] == '(':
                raise ValueError("Несоответствие скобок в выражении.")
            output.append(operators.pop())

        return ''.join(output)

    def postfix_to_nfa(self, postfix):
        stack = []
        print(postfix)
        for char in postfix:
            if char == '*':
                nfa = stack.pop()
                stack.append(nfa.kleene_star())
            elif char == '+':
                nfa = stack.pop()
                stack.append(nfa.plus())
            elif char == '|':
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                stack.append(nfa1.union(nfa2))
            elif char == '.':
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                stack.append(nfa1.concatenate(nfa2))
            else:
                stack.append(NFA.for_symbol(char))
        if len(stack) != 1:
            raise ValueError("Ошибка в разборе регулярного выражения.")
        return stack.pop()

    def nfa_to_table(self, nfa):
        states = list()
        transitions = {}

        # Сбор всех состояний НКА
        def collect_states(state):
            if state not in states:
                states.append(state)
                for symbol, targets in state.transitions.items():
                    for target in targets:
                        collect_states(target)
                for target in state.epsilon_transitions:
                    collect_states(target)

        collect_states(nfa.start_state)
        state_to_name = {nfa.start_state: "q0"}
        for i, state in enumerate(states):
            if state != nfa.start_state:
                state_to_name[state] = f"q{i}"

        header_row = [""] + [state_to_name[s] for s in states]

        symbols = set()
        for state in states:
            for symbol in state.transitions.keys():
                symbols.add(symbol)

        symbols = sorted(symbols) + ["ε"]

        table = []
        for symbol in symbols:
            row = [symbol]
            for state in states:
                if symbol in state.transitions:
                    targets = state.transitions[symbol]
                    row.append(",".join(state_to_name[t] for t in targets))
                elif symbol == "ε":
                    row.append(",".join(state_to_name[t] for t in state.epsilon_transitions))
                else:
                    row.append("")
            table.append(row)

        final_row = []
        final_row.append("")
        for state in states:
            if state == nfa.accept_state:
                final_row.append("F")
            else:
                final_row.append("")

        result = [";".join(final_row), ";".join(header_row)]
        result += [";".join(row) for row in table]

        return "\n".join(result)

