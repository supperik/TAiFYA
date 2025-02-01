import sys
from dataclasses import dataclass, field


@dataclass
class State:
    id: int
    is_final: bool = False
    transitions: dict[str, set[int]] = field(default_factory=dict)


@dataclass
class NFA:
    states: list[State]
    start_state: int
    final_states: set[int]
    alphabet: set[str]


class RegexToNFA:
    def __init__(self):
        self.state_counter = 0

    def create_new_state(self) -> State:
        state = State(self.state_counter)
        self.state_counter += 1
        return state

    def build_nfa(self, regex: str) -> NFA:
        if not regex:
            return self.build_basic('')

        tokens = self.tokenize(regex)
        operators = []
        operands = []

        def process_operator(op):
            if op == '|':
                if len(operands) >= 2:
                    nfa2 = operands.pop()
                    nfa1 = operands.pop()
                    operands.append(self.build_union(nfa1, nfa2))
            elif op == '.':
                if len(operands) >= 2:
                    nfa2 = operands.pop()
                    nfa1 = operands.pop()
                    operands.append(self.build_concatenation(nfa1, nfa2))
            elif op == '*':
                if operands:
                    nfa = operands.pop()
                    operands.append(self.build_star(nfa))
            elif op == '+':
                if operands:
                    nfa = operands.pop()
                    operands.append(self.build_plus(nfa))

        for token in tokens:
            if token == '(':
                operators.append(token)
            elif token == ')':
                while operators and operators[-1] != '(':
                    process_operator(operators.pop())
                # Remove '('
                if operators:
                    operators.pop()
            elif token in ['|', '.', '*', '+']:
                # Process operators with higher or equal priority
                while operators and operators[-1] != '(' and (
                        (token == '|' and operators[-1] in ['.', '*', '+']) or
                        (token == '.' and operators[-1] in ['*', '+']) or
                        (token in ['*', '+'] and operators[-1] in ['*', '+'])):
                    process_operator(operators.pop())
                operators.append(token)
            else:
                operands.append(self.build_basic(token))

        while operators:
            process_operator(operators.pop())

        return operands[0] if operands else self.build_basic('')

    def tokenize(self, regex: str) -> list[str]:
        tokens = []
        i = 0
        while i < len(regex):
            if regex[i] in ['(', ')', '*', '+', '|']:
                # Concatenation before '('
                if (regex[i] == '(' and i > 0 and regex[i - 1] not in ['(', '|']):
                    tokens.append('.')
                tokens.append(regex[i])
            elif regex[i] != " ":
                # Concatenation
                if i > 0 and regex[i - 1] not in ['(', '|'] and tokens and tokens[-1] not in ['(', '|', '.']:
                    tokens.append('.')
                tokens.append(regex[i])
            i += 1
        return tokens

    def build_basic(self, symbol: str) -> NFA:
        start = self.create_new_state()
        end = self.create_new_state()
        end.is_final = True
        start.transitions[symbol] = {end.id}
        return NFA([start, end], start.id, {end.id}, {symbol})

    def build_star(self, nfa: NFA) -> NFA:
        start = self.create_new_state()
        end = self.create_new_state()
        end.is_final = True

        start.transitions['ε'] = {nfa.start_state, end.id}

        for state in nfa.states:
            if state.id in nfa.final_states:
                state.transitions.setdefault('ε', set()).add(nfa.start_state)
                state.transitions.setdefault('ε', set()).add(end.id)

        nfa.alphabet.add('ε')
        return NFA([start] + nfa.states + [end], start.id, {end.id}, nfa.alphabet)

    def build_plus(self, nfa: NFA) -> NFA:
        start = self.create_new_state()
        end = self.create_new_state()
        end.is_final = True

        start.transitions['ε'] = {nfa.start_state}

        for state in nfa.states:
            if state.id in nfa.final_states:
                state.transitions.setdefault('ε', set()).add(end.id)
                state.transitions.setdefault('ε', set()).add(nfa.start_state)

        nfa.alphabet.add('ε')
        return NFA([start] + nfa.states + [end], start.id, {end.id}, nfa.alphabet)

    def build_union(self, nfa1: NFA, nfa2: NFA) -> NFA:
        old_counter = self.state_counter
        self.state_counter = 0

        new_states: list[State] = []
        start = State(0)
        new_states.append(start)

        # Copy states from nfa1 and nfa2
        nfa1_map: dict[int, int] = {}
        for old_state in nfa1.states:
            new_state = State(len(new_states))
            new_state.transitions = dict(old_state.transitions)
            nfa1_map[old_state.id] = new_state.id
            new_states.append(new_state)

        nfa2_map: dict[int, int] = {}
        for old_state in nfa2.states:
            new_state = State(len(new_states))
            new_state.transitions = dict(old_state.transitions)
            nfa2_map[old_state.id] = new_state.id
            new_states.append(new_state)

        end = State(len(new_states))
        end.is_final = True
        new_states.append(end)

        # ε-transitions from new start to both nfa starts
        start.transitions['ε'] = {nfa1_map[nfa1.start_state], nfa2_map[nfa2.start_state]}

        # Remap transitions from nfa1 and nfa2 + add transitions to new end state
        for old_id, new_id in nfa1_map.items():
            state = new_states[new_id]
            new_transitions = {}
            for symbol, targets in state.transitions.items():
                new_transitions[symbol] = {nfa1_map[t] for t in targets}
            state.transitions = new_transitions
            if old_id in nfa1.final_states:
                state.transitions.setdefault('ε', set()).add(end.id)

        for old_id, new_id in nfa2_map.items():
            state = new_states[new_id]
            new_transitions = {}
            for symbol, targets in state.transitions.items():
                new_transitions[symbol] = {nfa2_map[t] for t in targets}
            state.transitions = new_transitions
            if old_id in nfa2.final_states:
                state.transitions.setdefault('ε', set()).add(end.id)

        self.state_counter = max(old_counter, len(new_states))

        alphabet = nfa1.alphabet | nfa2.alphabet | {'ε'}
        return NFA(new_states, start.id, {end.id}, alphabet)

    def build_concatenation(self, nfa1: NFA, nfa2: NFA) -> NFA:
        old_counter = self.state_counter
        self.state_counter = 0

        new_states: list[State] = []

        # Copy states from nfa1 and nfa2
        nfa1_map: dict[int, int] = {}
        for idx, old_state in enumerate(nfa1.states):
            new_state = State(idx)
            new_state.transitions = dict(old_state.transitions)
            nfa1_map[old_state.id] = new_state.id
            new_states.append(new_state)

        base_idx = len(new_states)
        nfa2_map: dict[int, int] = {}
        for idx, old_state in enumerate(nfa2.states):
            new_state = State(base_idx + idx)
            new_state.transitions = dict(old_state.transitions)
            nfa2_map[old_state.id] = new_state.id
            new_states.append(new_state)

        # Update transitions
        for state in new_states[:base_idx]:
            new_transitions = {}
            for symbol, targets in state.transitions.items():
                new_transitions[symbol] = {nfa1_map[t] for t in targets}
            state.transitions = new_transitions

        for state in new_states[base_idx:]:
            new_transitions = {}
            for symbol, targets in state.transitions.items():
                new_transitions[symbol] = {nfa2_map[t] for t in targets}
            state.transitions = new_transitions

        # Add ε-transitions from nfa1 final states to nfa2 start state
        for old_id in nfa1.final_states:
            new_states[nfa1_map[old_id]].transitions.setdefault('ε', set()).add(nfa2_map[nfa2.start_state])

        final_states = {nfa2_map[state_id] for state_id in nfa2.final_states}
        self.state_counter = max(old_counter, len(new_states))

        alphabet = nfa1.alphabet | nfa2.alphabet | {'ε'}
        return NFA(new_states, nfa1_map[nfa1.start_state], final_states, alphabet)


def write_nfa_to_file(filename: str, nfa: NFA, states: list[State]):
    with open(filename, 'w', encoding="utf-8") as f:
        state_names = [f'S{s.id}' for s in nfa.states]

        # F line
        f.write(';' * len(state_names) + 'F\n')

        # States line
        f.write(';' + ';'.join(state_names) + '\n')

        # Transitions line
        alphabet = sorted(list(nfa.alphabet - {'ε'})) + ['ε']
        for symbol in alphabet:
            line = [symbol]
            for s in states:
                transitions = []
                for state in nfa.states:
                    if state.id == s.id and symbol in state.transitions:
                        transitions.extend(f'S{x}' for x in state.transitions[symbol])
                line.append(','.join(transitions) if transitions else '')
            f.write(';'.join(line) + '\n')


def main():
    nfa = RegexToNFA().build_nfa("cac*(ba)*|(ca)*cb*|a*|b*")
    write_nfa_to_file("output.txt", nfa, nfa.states)


if __name__ == "__main__":
    main()