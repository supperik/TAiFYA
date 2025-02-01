from State import State


class NFA:
    def __init__(self, start_state, accept_state):
        self.start_state = start_state
        self.accept_state = accept_state

    @staticmethod
    def for_symbol(symbol):
        start = State()
        accept = State()
        start.transitions[symbol] = [accept]
        return NFA(start, accept)

    @staticmethod
    def for_epsilon():
        start = State()
        accept = State()
        start.epsilon_transitions.append(accept)
        return NFA(start, accept)

    @staticmethod
    def for_empty():
        start = State()
        accept = State()
        return NFA(start, accept)

    def union(self, other):
        start = State()
        accept = State()
        start.epsilon_transitions.extend([self.start_state, other.start_state])
        self.accept_state.epsilon_transitions.append(accept)
        other.accept_state.epsilon_transitions.append(accept)
        return NFA(start, accept)

    def concatenate(self, other):
        self.accept_state.epsilon_transitions.append(other.start_state)
        return NFA(self.start_state, other.accept_state)

    def kleene_star(self):
        start = State()
        accept = State()
        start.epsilon_transitions.extend([self.start_state, accept])
        self.accept_state.epsilon_transitions.extend([self.start_state, accept])
        return NFA(start, accept)

    def plus(self):
        start = State()
        accept = State()
        start.epsilon_transitions.append(self.start_state)
        self.accept_state.epsilon_transitions.extend([self.start_state, accept])
        return NFA(start, accept)

