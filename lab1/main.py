from convert_machine import read_file_and_fill_lists, convert_mili_machine_to_mura


input_file = 'input.txt'

all_transitions_mili = []
states_mili = []
states_mili_equal_mura = {}
states_mura = []
states_mura_has_transitions = {}
states_mili_has_transitions = {}

read_file_mili_and_fill_lists(input_file, all_transitions_mili, states_mili, states_mili_equal_mura, states_mura,
                         states_mura_has_transitions, states_mili_has_transitions)

convert_mili_machine_to_mura(states_mili_equal_mura, states_mura, states_mili_has_transitions)
