from NFAMachine import NFA


class RegexToNFA:
    def __init__(self):
        self.state_counter = 0

    def new_state(self):
        """Создает уникальное состояние."""
        state = f"q{self.state_counter}"
        self.state_counter += 1
        return state

    def regex_to_nfa(self, regex):
        """Конвертирует регулярное выражение в NFA."""
        regex = self.add_concatenation_operator(regex)
        postfix = self.infix_to_postfix(regex)
        return self.postfix_to_nfa(postfix)

    def add_concatenation_operator(self, regex):
        """Добавляет явный оператор конкатенации (.) в регулярное выражение."""
        result = []
        for i in range(len(regex) - 1):
            result.append(regex[i])
            if (
                    regex[i] not in "|("
                    and regex[i + 1] not in "|)*+"
            ):
                result.append(".")
        result.append(regex[-1])
        return "".join(result)

    def infix_to_postfix(self, regex):
        """Конвертирует инфиксное регулярное выражение в постфиксное."""
        precedence = {'|': 1, '.': 2, '*': 3, '+': 3}
        output = []
        stack = []

        for char in regex:
            if char.isalnum():  # Символы
                output.append(char)
            elif char == '(':
                stack.append(char)
            elif char == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()  # Убираем '('
            else:  # Операторы
                while stack and precedence.get(stack[-1], 0) >= precedence.get(char, 0):
                    output.append(stack.pop())
                stack.append(char)

        while stack:
            output.append(stack.pop())

        return "".join(output)

    def postfix_to_nfa(self, postfix):
        """Создает NFA из постфиксного регулярного выражения."""
        stack = []
        for char in postfix:
            if char.isalnum():
                stack.append(self.build_basic_nfa(char))
            elif char == '.':
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                stack.append(self.build_concatenation_nfa(nfa1, nfa2))
            elif char == '|':
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                stack.append(self.build_union_nfa(nfa1, nfa2))
            elif char == '*':
                nfa = stack.pop()
                stack.append(self.build_kleene_star_nfa(nfa))

        return stack.pop()

    def build_basic_nfa(self, symbol):
        """Создает базовый NFA для символа."""
        start = self.new_state()
        accept = self.new_state()
        states = {start, accept}
        inputs = {symbol}
        transitions = {(start, symbol): {accept}}
        return NFA(states, inputs, transitions, start)

    def build_concatenation_nfa(self, nfa1, nfa2):
        """Создает NFA для конкатенации."""
        states = nfa1.states | nfa2.states
        inputs = nfa1.inputs | nfa2.inputs
        transitions = {**nfa1.transitions, **nfa2.transitions}
        transitions.setdefault((nfa1.start_state, ''), set()).add(nfa2.start_state)
        start_state = nfa1.start_state
        return NFA(states, inputs, transitions, start_state)

    def build_union_nfa(self, nfa1, nfa2):
        """Создает NFA для объединения (|)."""
        start = self.new_state()
        accept = self.new_state()
        states = nfa1.states | nfa2.states | {start, accept}
        inputs = nfa1.inputs | nfa2.inputs
        transitions = {**nfa1.transitions, **nfa2.transitions}
        transitions.setdefault((start, ''), set()).update({nfa1.start_state, nfa2.start_state})
        for state in [nfa1.start_state, nfa2.start_state]:
            transitions.setdefault((state, ''), set()).add(accept)
        return NFA(states, inputs, transitions, start)

    def build_kleene_star_nfa(self, nfa):
        """Создает NFA для замыкания Клини (*)."""
        start = self.new_state()
        accept = self.new_state()
        states = nfa.states | {start, accept}
        inputs = nfa.inputs
        transitions = nfa.transitions.copy()
        transitions.setdefault((start, ''), set()).update({nfa.start_state, accept})
        transitions.setdefault((nfa.start_state, ''), set()).update({accept, nfa.start_state})
        return NFA(states, inputs, transitions, start)
