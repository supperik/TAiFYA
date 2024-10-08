# Перевод автомата Мили в Мура

def read_file_mili_and_fill_lists(input_file: str):
    with open(input_file, 'r') as in_file:
        lines = in_file.readlines()

        states_mili = [item.rstrip() for item in lines[0].split(';')[1:]]

        transitions_mili = []
        states_mili_has_transitions = {}

        for state_mili in states_mili:
            states_mili_has_transitions[state_mili] = []

        for line in lines[1:]:
            line_list = line.split(';')

            local_transitions = []
            for j in range(1, len(line_list)):
                transition_mili = line_list[j].rstrip()

                states_mili_has_transitions[states_mili[j - 1]].append(transition_mili)

                local_transitions.append(transition_mili)
            transitions_mili.append(local_transitions)

    all_transitions_mili = []

    for transitions_mili_lists in transitions_mili:
        all_transitions_mili += transitions_mili_lists

    all_transitions_mili = list(set(all_transitions_mili))
    all_transitions_mili.sort()

    states_mura = []

    for i in range(len(list(set(all_transitions_mili)))):
        states_mura.append(f'q{i}')

    states_mili_equal_mura = {}

    for i in range(len(list(set(all_transitions_mili)))):
        states_mili_equal_mura[all_transitions_mili[i]] = f'q{i}'

    states_mura_has_transitions = {}

    for state_mura in states_mura:
        states_mura_has_transitions[state_mura] = []

    out_signals = []

    for transition in all_transitions_mili:
        out_signals.append(transition.split('/')[1])

    # print(f'all_transitions_mili        {all_transitions_mili}')
    # print(f'states_mili                 {states_mili}')
    # print(f'states_mili_equal_mura      {states_mili_equal_mura}')
    # print(f'states_mura                 {states_mura}')
    # print(f'states_mura_has_transitions {states_mura_has_transitions}')
    # print(f'states_mili_has_transitions {states_mili_has_transitions}')
    # print(f'out_signas                  {out_signals}')

    return states_mili_equal_mura, states_mura, states_mili_has_transitions, states_mura_has_transitions, out_signals


def read_file_mura_and_fill_lists(input_file: str):
    with open(input_file, "r") as in_file:
        lines = in_file.readlines()
        out_signals = [item.rstrip() for item in lines[0].split(';')[1:]]
        states_mura = [item.rstrip() for item in lines[1].split(';')[1:]]

        transitions_mura = []
        for line in lines[2:]:
            transitions_mura += [[item.rstrip() for item in line.split(';')[1:]]]

        states_mura_has_transitions_and_out_signals = {
            states_mura[i]: [
                [transitions_mura[j][i] for j in range(len(transitions_mura))],
                out_signals[i]]
            for i in range(len(out_signals)) if len(out_signals) == len(states_mura)}

    return states_mura_has_transitions_and_out_signals


def convert_mili_machine_to_mura(states_mili_equal_mura: dict,
                                 states_mura: list,
                                 states_mili_has_transitions: dict,
                                 states_mura_has_transitions: dict,
                                 out_signals: list):
    for state_mura in states_mura:
        state_mili_equal_mura = get_key(states_mili_equal_mura, state_mura).split('/')[0]
        state_mura_equal_mili_transitions = []

        for transition_mili_from_state_mili in states_mili_has_transitions[state_mili_equal_mura]:
            state_mura_equal_mili_transitions.append(states_mili_equal_mura[transition_mili_from_state_mili])

        states_mura_has_transitions[state_mura].append(state_mura_equal_mili_transitions)
        states_mura_has_transitions[state_mura].append(out_signals[states_mura.index(state_mura)])
    print(states_mura_has_transitions)


def convert_mura_machine_to_mili(states_mura_has_transitions_and_out_signals: dict):
    states_mili_has_transitions = {}

    for state_mura, transitions_and_out_signals in states_mura_has_transitions_and_out_signals.items():
        transitions, current_signal = transitions_and_out_signals
        new_transitions = []

        for state in transitions:
            signal = states_mura_has_transitions_and_out_signals[state][1]
            new_transitions.append(f'{state}/{signal}')

        states_mili_has_transitions[state_mura] = new_transitions

    print(states_mili_has_transitions)


def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k
