import itertools


def split_regex(regex_for_split: str) -> list[str]:
    tokens = []
    i = 0
    while i < len(regex_for_split):
        if regex_for_split[i] in ['(', ')', '*', '+', '|']:
            if regex_for_split[i] == '(' and i > 0 and regex_for_split[i - 1] not in ['(', '|']:
                tokens.append('.')
            tokens.append(regex_for_split[i])
        elif regex_for_split[i] != " ":
            if i > 0 and regex_for_split[i - 1] not in ['(', '|'] and tokens and tokens[-1] not in ['(', '|', '.']:
                tokens.append('-')
            tokens.append(regex_for_split[i])
        i += 1
    return tokens


class RegexToNFA:
    def __init__(self, regex):
        self.regex = regex#''.join(split_regex(regex))
        self.state_counter = itertools.count()  # Counter for unique state names
        self.transitions = {}  # Dictionary to hold transitions
        self.start_state = None
        self.final_states = set()

    def new_state(self):
        """Create a new unique state."""
        state = f"q{next(self.state_counter)}"
        self.transitions[state] = {}
        return state

    def build_nfa(self):
        """Main method to parse regex and construct NFA transitions."""
        # self.start_state, end_state = self._parse_regex(self.regex)
        self._parse_regex(self.regex)
        # self.final_states.add(end_state)
        # return self._generate_table()

    def _parse_regex(self, regex):
        i = 0
        states = list()
        while i < len(regex):
            char = regex[i]
            print(regex[i:])
            states = []
            if char == '*' or char == '+':
                # states.append(self._handle_closure(regex))
                # i += 1
                pass
            if char == '(':
                bracket_counter = 0
                substring = regex[i + 1:]
                for j in range(len(substring)):
                    substring_char = substring[j]
                    if substring_char == '(':
                        bracket_counter += 1
                    if substring_char == ')' and bracket_counter == 0:
                        # print(substring[:j])
                        # print(regex[i + 1:i + 1 + j])
                        states.append(self._parse_regex(regex[i + 1:i + 1 + j]))
                        i = i + 1 + j
                        break
                    elif substring_char == ')':
                        bracket_counter -= 1
            elif char == '|':
                part1 = regex[0:i]
                part2 = regex[i + 1:-1]
                print('part1: ', part1, ' part2: ', part2)
                states.append(self._handle_union([part1, part2]))
            else:

            # elif char == '-':
            #     print('-: ', regex[i + 1])
            #     states.append(self._handle_concatenation(regex[i + 1]))

            # print(states)
            print(i)
            i += 1

    def _handle_union(self, parts):
        """Handle the union (|) operator."""
        # start = self.new_state()
        # end = self.new_state()
        #
        # for part in parts:
        #     if part != parts[0]:
        #         sub_start, sub_end = self._parse_regex(part)
        #     self._add_transition(start, 'ε', sub_start)
        #     self._add_transition(sub_end, 'ε', end)

        return start, end

    def _handle_group(self, regex):
        """Handle groups within parentheses."""
        # inner = regex[regex.find('(') + 1:regex.rfind(')')]  # Extract inside parentheses
        # start, end = self._parse_regex(inner)
        # return start, end

    def _handle_closure(self, regex, start_state = None):
        """Handle closure (* or +)."""
        # base = regex[:-1]  # Remove the operator (* or +)
        # start = self.new_state()
        # end = self.new_state()
        #
        # sub_start, sub_end = self._parse_regex(base)
        # self._add_transition(start, 'ε', sub_start)
        # self._add_transition(sub_end, 'ε', end)
        #
        # if regex.endswith('*'):
        #     self._add_transition(sub_end, 'ε', sub_start)  # Loop back
        #     self._add_transition(start, 'ε', end)  # Skip entirely
        #
        # if regex.endswith('+'):
        #     self._add_transition(sub_end, 'ε', sub_start)  # Loop back only
        #
        # return start, end

    def _handle_concatenation(self, char):
        """Handle concatenation of symbols."""
        # start = None
        # previous_end = None
        #
        # sub_start = self.new_state()
        # sub_end = self.new_state()
        # self._add_transition(sub_start, char, sub_end)
        #
        # if start is None:
        #     start = sub_start
        #
        # if previous_end is not None:
        #     self._add_transition(previous_end, 'ε', sub_start)

        # i = 0
        # while i < len(regex):
        #     char = regex[i]
        #
        #     if char == '(':
        #         # Find the matching closing parenthesis
        #         open_count = 1
        #         for j in range(i + 1, len(regex)):
        #             if regex[j] == '(':
        #                 open_count += 1
        #             elif regex[j] == ')':
        #                 open_count -= 1
        #             if open_count == 0:
        #                 break
        #         sub_start, sub_end = self._parse_regex(regex[i + 1:j])
        #         i = j
        #     elif i + 1 < len(regex) and regex[i + 1] in '*+':
        #         sub_start, sub_end = self._handle_closure(regex[i:i + 2])
        #         i += 1
        #     else:
        #         sub_start = self.new_state()
        #         sub_end = self.new_state()
        #         self._add_transition(sub_start, char, sub_end)
        #
            # if start is None:
            #     start = sub_start
            #
            # if previous_end is not None:
            #     self._add_transition(previous_end, 'ε', sub_start)
        #
        #     previous_end = sub_end
        #     i += 1

        return start, previous_end

    def _add_transition(self, from_state, symbol, to_state):
        """Add a transition to the NFA."""
        if symbol not in self.transitions[from_state]:
            self.transitions[from_state][symbol] = []
        self.transitions[from_state][symbol].append(to_state)

    def _generate_table(self):
        """Generate the NFA transition table in the specified format."""
        all_states = sorted(self.transitions.keys())
        symbols = sorted(set(sym for trans in self.transitions.values() for sym in trans))

        # Table header
        table = [';' + ';'.join(all_states)]

        for symbol in symbols:
            row = [symbol]
            for state in all_states:
                if symbol in self.transitions[state]:
                    row.append(','.join(self.transitions[state][symbol]))
                else:
                    row.append('')
            table.append(';'.join(row))

        return '\n'.join(table)


# Example usage
regex = "cac*(ba)*|(ca)*cb*|a*|b*"
converter = RegexToNFA(regex)
# nfa_table = converter.build_nfa()
converter.build_nfa()
# print(nfa_table)
