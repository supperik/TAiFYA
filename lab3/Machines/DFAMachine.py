from pyvis.network import Network
import re


class DFA:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

    @classmethod
    def from_nfa(cls, nfa):
        def epsilon_closure(state, transitions):
            closure = {state}
            stack = [state]
            while stack:
                current = stack.pop()
                if (current, 'ε') in transitions:  # Проверяем ε-переходы
                    for next_state in transitions[(current, 'ε')]:
                        if next_state not in closure:
                            closure.add(next_state)
                            stack.append(next_state)
            return closure

        def epsilon_closure_of_set(state_set, transitions):
            closure = set()
            for state in state_set:
                closure.update(epsilon_closure(state, transitions))
            return closure

        dfa_states = {}
        dfa_alphabet = sorted(set(nfa.inputs) - {'ε'})
        dfa_transitions = {}
        dfa_start_state = frozenset(
            epsilon_closure(nfa.start_state, nfa.transitions))  # ε-замыкание стартового состояния
        dfa_accept_states = set()

        unprocessed_states = [dfa_start_state]
        processed_states = set()
        state_counter = 0

        dfa_states[dfa_start_state] = f"q{state_counter}"
        state_counter += 1

        nfa_accept_states = {state for state in nfa.states if state in nfa.accept_states}

        while unprocessed_states:
            current = unprocessed_states.pop()
            processed_states.add(current)

            current_name = dfa_states[current]
            dfa_transitions[current_name] = {}

            if any(state in nfa_accept_states for state in current):
                dfa_accept_states.add(current_name)

            for symbol in dfa_alphabet:
                next_state = set()
                for substate in current:
                    if (substate, symbol) in nfa.transitions:
                        next_state.update(nfa.transitions[(substate, symbol)])

                next_state = epsilon_closure_of_set(next_state, nfa.transitions)
                next_state = frozenset(next_state)

                if next_state:
                    if next_state not in dfa_states:
                        dfa_states[next_state] = f"q{state_counter}"
                        state_counter += 1
                        unprocessed_states.append(next_state)

                    next_state_name = dfa_states[next_state]
                    dfa_transitions[current_name][symbol] = next_state_name
                else:
                    dfa_transitions[current_name][symbol] = "-"

        return cls(
            states=set(dfa_states.values()),
            alphabet=list(dfa_alphabet),
            transitions=dfa_transitions,
            start_state=dfa_states[dfa_start_state],
            accept_states=dfa_accept_states
        )

    import re

    def to_table(self):
        def extract_number(state):
            return int(re.search(r'\d+', state).group())

        sorted_states = sorted(self.states, key=extract_number)

        header = [""] + sorted_states
        rows = []

        for symbol in self.alphabet:
            row = [symbol]
            for state in sorted_states:
                row.append(self.transitions[state].get(symbol, "-"))
            rows.append(row)

        final_row = [""]
        for state in sorted_states:
            if state in self.accept_states:
                final_row.append("F")
            else:
                final_row.append("")

        result = [";".join(final_row), ";".join(header)]

        table = '\n'.join(result)
        for row in rows:
            table += '\n' + ';'.join(row)
        return table

    def __str__(self):
        return self.to_table()

    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            file.write(self.to_table())

    def draw_dfa(self, output_filename):
        # Создаем объект для визуализации графа
        net = Network(directed=True)

        # Добавляем узлы для состояний
        for state in self.states:
            if state == self.start_state:  # Выделяем стартовое состояние, например, красным
                net.add_node(state, label=state, color="red")  # Цвет для стартового состояния
            elif state.endswith('(end)'):
                net.add_node(state, label=state, color="green")
            else:
                net.add_node(state, label=state)

        # Добавляем рёбра (переходы) между состояниями
        for src, transitions_dict in self.transitions.items():
            for symbol, state in transitions_dict.items():
                if transitions_dict[symbol] != '-':
                    net.add_edge(src, state, label=symbol)  # Переход подписан символом

        # Дополнительные опции для улучшения визуализации
        net.set_options("""
            var options = {
                "edges": {
                    "color": {
                        "inherit": true
                    },
                    "smooth": false
                }
            }
        """)

        # Сохраняем граф в файл
        net.save_graph(output_filename)
