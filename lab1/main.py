from Machines.MealyMachine import MealyMachine
from Machines.MooreMachine import MooreMachine

# input_file_mealy = 'input.txt'
input_file_moore = 'input1.txt'

# mealy = MealyMachine.from_file(input_file_mealy)
# moore_data = mealy.convert_to_moore_machine()
# print(mealy)
# mealy.draw_mealy_machine()

moore = MooreMachine.from_file(input_file_moore)
print(moore)
# moore.draw_moore_machine()

mealy_data = moore.convert_to_mealy_machine()
mealy = MealyMachine.from_dict(mealy_data)
print(mealy)
# mealy.draw_mealy_machine()
