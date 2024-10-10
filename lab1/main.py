from Machines.MealyMachine import MealyMachine
from Machines.MooreMachine import MooreMachine

input_file_mealy = 'input.txt'
input_file_moore = 'input1.txt'

mealy = MealyMachine.from_file(input_file_mealy)
moore = MooreMachine.from_file(input_file_moore)
print(moore)
print(mealy)

mealy.draw_mealy_machine()
