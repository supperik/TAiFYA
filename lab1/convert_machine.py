# Перевод автомата Мили в Мура

def read_file_mili_and_fill_lists(input_file: str,
                             all_transitions_mili: list,
                             states_mili: list,
                             states_mili_equal_mura: dict,
                             states_mura: list,
                             states_mura_has_transitions: dict,
                             states_mili_has_transitions: dict):

    with open(input_file, 'r') as in_file:
        lines = in_file.readlines()
        states_mili += [item.rstrip() for item in lines[0].split(';')[1:]]
        transitions_mili = []
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

    for lists in transitions_mili:
        all_transitions_mili += lists
    all_transitions_mili = list(set(all_transitions_mili))
    all_transitions_mili.sort()

    for i in range(len(list(set(all_transitions_mili)))):
        states_mura.append(f'q{i}')

    for i in range(len(list(set(all_transitions_mili)))):
        states_mili_equal_mura[all_transitions_mili[i]] = f'q{i}'

    for state_mura in states_mura:
        states_mura_has_transitions[state_mura] = []

    # print(f'all_transitions_mili        {all_transitions_mili}')
    # print(f'states_mili                 {states_mili}')
    # print(f'states_mili_equal_mura      {states_mili_equal_mura}')
    # print(f'states_mura                 {states_mura}')
    # print(f'states_mura_has_transitions {states_mura_has_transitions}')
    # print(f'states_mili_has_transitions {states_mili_has_transitions}')


def convert_mili_machine_to_mura(states_mili_equal_mura: dict,
                                 states_mura: list,
                                 states_mili_has_transitions: dict):
    for state_mura in states_mura:
        state_mili_equal_mura = get_key(states_mili_equal_mura, state_mura).split('/')[0]
        for transition_mili_from_state_mili in states_mili_has_transitions[state_mili_equal_mura]:
            state_mura_equal_mili_transition = states_mili_equal_mura[transition_mili_from_state_mili]
            print(state_mura_equal_mili_transition, end=' ')
        print()

def convert_mura_machine_to_mili():
    pass

def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k