import json
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network


class MooreMachine:
    def __init__(self, moore_machine_data):
        self.moore_machine_data = moore_machine_data

    def __str__(self):
        col_width = max(len(state) for state in self.moore_machine_data.keys()) + 2
        trans_width = max(len(transition) for transitions in self.moore_machine_data.values() for transition in
                          transitions[0]) + 2
        output_width = max(len(output) for _, output in self.moore_machine_data.values()) + 2

        input_symbols = [f'x{i + 1}' for i in range(len(next(iter(self.moore_machine_data.values()))[0]))]
        header = "State".ljust(col_width) + "Output".center(output_width) + ''.join(
            input_symbol.center(trans_width) for input_symbol in input_symbols)
        table = header + "\n" + "-" * len(header) + "\n"

        for state, (transitions, output_signal) in self.moore_machine_data.items():
            row = state.ljust(col_width)
            row += output_signal.center(output_width)
            row += ''.join(transition.center(trans_width) for transition in transitions)
            table += row + "\n"

        return table

    @classmethod
    def from_file(cls, filename: str):
        with open(filename, "r") as in_file:
            lines = in_file.readlines()
            out_signals = [item.rstrip() for item in lines[0].split(';')[1:]]
            states_moore = [item.rstrip() for item in lines[1].split(';')[1:]]

            transitions_moore = []
            for line in lines[2:]:
                transitions = []
                # for item in line.split(';')[1:]:
                #     if item != '':
                #         transitions += [item.rstrip()]
                # transitions_moore.append(transitions)
                transitions_moore += [[item.rstrip() for item in line.split(';')[1:]]]

            states_moore_has_transitions_and_out_signals = {}
            print(out_signals)

            if len(out_signals) == len(states_moore):
                for i in range(len(out_signals)):
                    transitions = []
                    for j in range(len(transitions_moore)):
                        # print(transitions_moore[j][i])
                        if transitions_moore[j][i] != '':
                            transitions.append(transitions_moore[j][i])

                    states_moore_has_transitions_and_out_signals[states_moore[i]] = [transitions, out_signals[i]]

            # states_moore_has_transitions_and_out_signals = {
            #     states_moore[i]: [
            #         [transitions_moore[j][i] for j in range(len(transitions_moore))],
            #         out_signals[i]]
            #     for i in range(len(out_signals)) if len(out_signals) == len(states_moore)}

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
                new_transitions.append(f's{state[1:]}/{signal}')
            state_moore = 's' + state_moore[1:]
            mealy_machine_data[state_moore] = new_transitions
        return mealy_machine_data

    def serialize_moore_machine(self, moore_machine_json_filepath: str = 'moore_machine.json'):
        moore_machine_json_data = json.dumps(self.moore_machine_data)
        with open(moore_machine_json_filepath, 'w') as moore_json_file:
            moore_json_file.write(moore_machine_json_data)

    def minimize_moore_machine(self):
        groups = {}
        for state, (transitions, output) in self.moore_machine_data.items():
            if output not in groups:
                groups[output] = []
            groups[output].append(state)

        partition = list(groups.values())

        def get_group(group_state, group_partition):
            for i, enum_group in enumerate(group_partition):
                if group_state in enum_group:
                    return i
            return -1

        minimized = False
        while not minimized:
            new_partition = []
            minimized = True

            for group in partition:
                subgroups = {}

                for state in group:
                    signature = tuple(get_group(target, partition) for target in self.moore_machine_data[state][0])
                    if signature not in subgroups:
                        subgroups[signature] = []
                    subgroups[signature].append(state)

                if len(subgroups) > 1:
                    minimized = False

                new_partition.extend(subgroups.values())

            partition = new_partition

        minimized_machine = {}
        for group in partition:
            representative = group[0]
            transitions = []
            for target in self.moore_machine_data[representative][0]:
                transitions.append(get_group(target, partition))
            output = self.moore_machine_data[representative][1]
            minimized_machine[f"s{partition.index(group)}"] = [[f's{transition}' for transition in transitions], output]

        return minimized_machine

    def draw_moore_machine(self, output_filename: str):
        state_transition_pairs = []
        moore_states_and_output_signal = []
        state_transition_pairs_with_input_output_signals = {}

        for state, transitions_and_output_signal in self.moore_machine_data.items():
            moore_states_and_output_signal.append(f'{state}/{transitions_and_output_signal[1]}')
            for i in range(len(transitions_and_output_signal[0])):
                transition_target = transitions_and_output_signal[0][i]
                state_transition_pairs.append(
                    (f'{state}/{transitions_and_output_signal[1]}',
                     f'{transition_target}/{self.moore_machine_data[transition_target][1]}')
                )
                state_transition_pairs_with_input_output_signals[
                    state_transition_pairs[-1]] = f"x{i + 1}"

        net = Network(directed=True)

        for state in moore_states_and_output_signal:
            net.add_node(state, label=state)

        for (src, dst) in state_transition_pairs:
            label = state_transition_pairs_with_input_output_signals[(src, dst)]
            net.add_edge(src, dst, label=label)

        net.set_options("""
                var options = {
                  "edges": {
                    "color": {
                      "inherit": true
                    },
                    "smooth": false
                  },
                  "physics": {
                    "enabled": true
                  }
                }
                """)

        net.save_graph(output_filename)

    def draw_minimized_moore_machine(self, minimized_moore_machine: dict, output_filename: str):
        state_transition_pairs = []
        moore_states_and_output_signal = []
        state_transition_pairs_with_input_output_signals = {}

        for state, transitions_and_output_signal in self.moore_machine_data.items():
            moore_states_and_output_signal.append(f'{state}/{transitions_and_output_signal[1]}')
            for i in range(len(transitions_and_output_signal[0])):
                transition_target = transitions_and_output_signal[0][i]
                state_transition_pairs.append(
                    (f'{state}/{transitions_and_output_signal[1]}',
                     f'{transition_target}/{self.moore_machine_data[transition_target][1]}')
                )
                state_transition_pairs_with_input_output_signals[
                    state_transition_pairs[-1]] = f"x{i + 1}"

        net = Network(directed=True)

        for state in moore_states_and_output_signal:
            net.add_node(state, label=f'Не минимизированный Мур {state}')

        for (src, dst) in state_transition_pairs:
            label = state_transition_pairs_with_input_output_signals[(src, dst)]
            net.add_edge(src, dst, label=label)

        state_transition_pairs = []
        moore_states_and_output_signal = []
        state_transition_pairs_with_input_output_signals = {}

        for state, transitions_and_output_signal in minimized_moore_machine.items():
            moore_states_and_output_signal.append(f'{state}/{transitions_and_output_signal[1]}')
            for i in range(len(transitions_and_output_signal[0])):
                transition_target = transitions_and_output_signal[0][i]
                state_transition_pairs.append(
                    (f'{state}/{transitions_and_output_signal[1]}',
                     f'{transition_target}/{minimized_moore_machine[transition_target][1]}')
                )
                state_transition_pairs_with_input_output_signals[
                    state_transition_pairs[-1]] = f"x{i + 1}"

        for state in moore_states_and_output_signal:
            net.add_node(state, label=f'Минимизированный Мур {state}')

        for (src, dst) in state_transition_pairs:
            label = state_transition_pairs_with_input_output_signals[(src, dst)]
            net.add_edge(src, dst, label=label)

        net.set_options("""
                var options = {
                  "edges": {
                    "color": {
                      "inherit": true
                    },
                    "smooth": false
                  },
                  "physics": {
                    "enabled": true
                  }
                }
                """)

        net.save_graph(output_filename)
    