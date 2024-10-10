import json


class MooreMachine:
    def __init__(self, moore_machine_data):
        self.moore_machine_data = moore_machine_data

    @classmethod
    def from_file(cls, filename: str):
        with open(filename, "r") as in_file:
            lines = in_file.readlines()
            out_signals = [item.rstrip() for item in lines[0].split(';')[1:]]
            states_moore = [item.rstrip() for item in lines[1].split(';')[1:]]

            transitions_moore = []
            for line in lines[2:]:
                transitions_moore += [[item.rstrip() for item in line.split(';')[1:]]]

            states_moore_has_transitions_and_out_signals = {
                states_moore[i]: [
                    [transitions_moore[j][i] for j in range(len(transitions_moore))],
                    out_signals[i]]
                for i in range(len(out_signals)) if len(out_signals) == len(states_moore)}

        return cls(states_moore_has_transitions_and_out_signals)

    @classmethod
    def from_json_file(cls, moore_machine_json_filepath: str = 'moore_machine.json'):
        with open(moore_machine_json_filepath, 'r') as moore_machine_json_file:
            moore_machine_data = json.load(moore_machine_json_file)
        return cls(moore_machine_data)

    @classmethod
    def from_dict(cls, moore_machine_dict: dict):
        return cls(moore_machine_dict)

    def convert_to_mealy_machine(self):
        mealy_machine_data = {}

        for state_moore, transitions_and_out_signals in self.moore_machine_data.items():
            transitions, current_signal = transitions_and_out_signals
            new_transitions = []

            for state in transitions:
                signal = self.moore_machine_data[state][1]
                new_transitions.append(f'{state}/{signal}')

            mealy_machine_data[state_moore] = new_transitions
        print(mealy_machine_data)
        return mealy_machine_data

    def serialize_moore_machine(self, moore_machine_json_filepath: str = 'moore_machine.json'):
        moore_machine_json_data = json.dumps(self.moore_machine_data)
        with open(moore_machine_json_filepath, 'w') as moore_json_file:
            moore_json_file.write(moore_machine_json_data)

    def __str__(self):
        return json.dumps(self.moore_machine_data)

    def draw_moore_machine(self):
        pass
