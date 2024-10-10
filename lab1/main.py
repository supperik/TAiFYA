from Machines.MealyMachine import MealyMachine
from Machines.MooreMachine import MooreMachine

# import convert_machine

input_file_mealy = 'input.txt'
input_file_moore = 'input1.txt'

# convert_machine.states_mili_equal_mura, states_mura, states_mili_has_transitions, states_mura_has_transitions, out_signals = (
#     convert_machine.read_file_mili_and_fill_lists(input_file_mealy))
# convert_machine.convert_mili_machine_to_mura(states_mili_equal_mura, states_mura, states_mili_has_transitions,
#                                              states_mura_has_transitions, out_signals)
#
# convert_mura_machine_to_mili(read_file_mura_and_fill_lists(input_file_mura))
#
# moore_dict = {'q0': [['q8', 'q3', 'q2'], 'y2'],
#               'q1': [['q8', 'q3', 'q2'], 'y4'],
#               'q2': [['q8', 'q3', 'q2'], 'y5'],
#               'q3': [['q0', 'q6', 'q4'], 'y1'],
#               'q4': [['q0', 'q6', 'q4'], 'y4'],
#               'q5': [['q0', 'q6', 'q4'], 'y5'],
#               'q6': [['q7', 'q1', 'q8'], 'y1'],
#               'q7': [['q7', 'q1', 'q8'], 'y3'],
#               'q8': [['q2', 'q9', 'q5'], 'y1'],
#               'q9': [['q2', 'q9', 'q5'], 'y2']}

mealy_dict = {'q0': ['q8/y1', 'q3/y1', 'q2/y5'],
              'q1': ['q8/y1', 'q3/y1', 'q2/y5'],
              'q2': ['q8/y1', 'q3/y1', 'q2/y5'],
              'q3': ['q0/y2', 'q6/y1', 'q4/y4'],
              'q4': ['q0/y2', 'q6/y1', 'q4/y4'],
              'q5': ['q0/y2', 'q6/y1', 'q4/y4'],
              'q6': ['q7/y3', 'q1/y4', 'q8/y1'],
              'q7': ['q7/y3', 'q1/y4', 'q8/y1'],
              'q8': ['q2/y5', 'q9/y2', 'q5/y5'],
              'q9': ['q2/y5', 'q9/y2', 'q5/y5']}
#
# mili = MiliMachine.from_file(input_file_mili)
# print(mili.mili_machine)
#
# mura = mili.convert_to_mura_machine()

mealy = MealyMachine.from_file(input_file_mealy)
# mealy.print_mealy_machine()

# moore = MooreMachine.from_json_file()
# moore.print_moore_machine()

# moore.convert_to_mealy_machine()
moore_dict = mealy.convert_to_moore_machine()
moore = MooreMachine.from_dict(moore_dict)
print(moore)
