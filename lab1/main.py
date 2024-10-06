from convert_machine import read_file_and_fill_lists, convert_mili_machine_to_mura


input_file = 'input.txt'

states_mili = []
transitions_mili = []
states_mili_has_transitions = {}

read_file_and_fill_lists(input_file, states_mili, transitions_mili, states_mili_has_transitions)

convert_mili_machine_to_mura(states_mili, transitions_mili, states_mili_has_transitions)
