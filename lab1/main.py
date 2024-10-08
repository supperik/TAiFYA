from convert_machine import read_file_mili_and_fill_lists, convert_mili_machine_to_mura, read_file_mura_and_fill_lists, \
    convert_mura_machine_to_mili

input_file_mili = 'input.txt'
input_file_mura = 'input1.txt'

states_mili_equal_mura, states_mura, states_mili_has_transitions, states_mura_has_transitions, out_signals = read_file_mili_and_fill_lists(input_file_mili)
convert_mili_machine_to_mura(states_mili_equal_mura, states_mura, states_mili_has_transitions, states_mura_has_transitions, out_signals)

convert_mura_machine_to_mili(read_file_mura_and_fill_lists(input_file_mura))
