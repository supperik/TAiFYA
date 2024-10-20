from Machines.MealyMachine import MealyMachine
from Machines.MooreMachine import MooreMachine

input_file_mealy = 'input.txt'
input_file_moore = 'input1.txt'

# mealy = MealyMachine.from_file(input_file_mealy)
# moore_data = mealy.convert_to_moore_machine()
# mealy.serialize_mealy_machine()
# print(mealy)
# mealy.draw_mealy_machine()

# moore = MooreMachine.from_file(input_file_moore)
# print(moore)
# moore.draw_moore_machine(output_filename="moore.html")
# minimized_moore_data = moore.minimize_moore_machine()

# minimized_moore = MooreMachine.from_dict(minimized_moore_data)
# print(minimized_moore)
# minimized_moore.draw_moore_machine(output_filename="minimized_moore.html")

mealy = MealyMachine.from_file(input_file_mealy)
print(mealy)
# mealy.draw_mealy_machine()
minimized_mealy_data = mealy.minimize_mealy_machine()
minimized_mealy = MealyMachine(minimized_mealy_data)
minimized_mealy.draw_mealy_machine(output_filename='minimized_mealy.html')
print(minimized_mealy)
