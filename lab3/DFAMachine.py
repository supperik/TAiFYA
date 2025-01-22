from pyvis.network import Network


class DFA:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state

    @classmethod
    def from_nfa(cls, nfa):
        dfa_states = {}
        dfa_alphabet = sorted(nfa.inputs)
        dfa_transitions = {}
        dfa_start_state = frozenset([nfa.start_state])
        if nfa.start_state == 'S':
            final_state = 'H'
        else:
            final_state = 'S'
        dfa_accept_states = set()

        unprocessed_states = [dfa_start_state]
        processed_states = set()
        state_counter = 0

        # Назначаем имя для стартового состояния
        dfa_states[dfa_start_state] = f"q{state_counter}"
        state_counter += 1

        nfa_accept_states = {state for state in nfa.states if (state, '') in nfa.transitions}

        while unprocessed_states:
            current = unprocessed_states.pop()
            processed_states.add(current)

            current_name = dfa_states[current]
            dfa_transitions[current_name] = {}

            # Определяем, если хотя бы одно из подсостояний DFA является конечным состоянием NFA
            if any(state in nfa_accept_states for state in current):
                dfa_accept_states.add(f"{current_name}(end)")  # Добавляем "(end)" к имени состояния

            for symbol in dfa_alphabet:
                next_state = set()
                for substate in current:
                    if (substate, symbol) in nfa.transitions:
                        next_state.update(nfa.transitions[(substate, symbol)])

                next_state = frozenset(next_state)
                if next_state:
                    if next_state not in dfa_states:
                        if final_state in next_state:
                            dfa_states[next_state] = f"q{state_counter}(end)"
                        else:
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

    def to_table(self):
        header = [" "] + sorted(self.states)
        rows = []

        for symbol in self.alphabet:
            row = [symbol]
            for state in sorted(self.states):
                row.append(self.transitions[state].get(symbol, "-"))
            rows.append(row)

        table = [header] + rows
        return "\n".join(";".join(str(cell) for cell in row) for row in table)

    def __str__(self):
        return self.to_table()

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
                },
                "physics": {
                    "enabled": true
                }
            }
        """)

        # Сохраняем граф в файл
        net.save_graph(output_filename)
