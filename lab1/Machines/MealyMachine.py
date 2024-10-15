import json
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network


class MealyMachine:
    def __init__(self, mealy_machine_data):  # создание объекта из словаря типа {state: [transitions, out_signal]}
        self.mealy_machine_data = mealy_machine_data

    def __str__(self):
        return json.dumps(self.mealy_machine_data)

    # Перегрузка конструктора, создание объекта путем чтения файла с данными автомата Мили
    @classmethod
    def from_file(cls, filename: str):
        with open(filename, 'r') as in_file:
            lines = in_file.readlines()
            states_mealy = [item.rstrip() for item in lines[0].split(';')[1:]]
            mealy_machine_data = {}

            for state_mealy in states_mealy:
                mealy_machine_data[state_mealy] = []

            for line in lines[1:]:
                line_list = line.split(';')

                for j in range(1, len(line_list)):
                    transition_mealy = line_list[j].rstrip()
                    mealy_machine_data[states_mealy[j - 1]].append(transition_mealy)

        return cls(mealy_machine_data)

    # Перегрузка конструктора, создание объекта из словаря формата, соответствующего типу автомата
    @classmethod
    def from_dict(cls, mealy_machine_dict: dict):
        return cls(mealy_machine_dict)

    # Перегрузка конструктора, создание объекта путем чтения файла с данными автомата Мили в формате json
    @classmethod
    def from_json_file(cls, mealy_machine_json_filepath: str = 'mealy_machine.json'):
        with open(mealy_machine_json_filepath, 'r') as mealy_machine_json_file:
            mealy_machine_data = json.load(mealy_machine_json_file)
        return cls(mealy_machine_data)

    def convert_to_moore_machine(self):
        moore_machine_data = {}

        def get_key(d, value):
            for k, v in d.items():
                if v == value:
                    return k

        all_transitions_mealy = []
        for state, transitions in self.mealy_machine_data.items():
            for transition in transitions:
                all_transitions_mealy.append(transition)
        all_transitions_mealy = list(set(all_transitions_mealy))
        all_transitions_mealy.sort()

        temp_transitions_list = []
        for transition in all_transitions_mealy:
            temp_transitions_list.append(transition.split('/')[0])

        for state_mealy in self.mealy_machine_data.keys():
            if state_mealy not in temp_transitions_list:
                all_transitions_mealy.insert(0, f'{state_mealy}/-')

        states_moore = []
        for i in range(len(list(set(all_transitions_mealy)))):
            states_moore.append(f'q{i}')

        for state_moore in states_moore:
            moore_machine_data[state_moore] = []

        out_signals = []
        for transition in all_transitions_mealy:
            out_signals.append(transition.split('/')[1])

        states_mealy_equal_moore = {}
        for i in range(len(list(set(all_transitions_mealy)))):
            states_mealy_equal_moore[all_transitions_mealy[i]] = f'q{i}'

        for state_moore in states_moore:
            state_mealy_equal_moore = get_key(states_mealy_equal_moore, state_moore).split('/')[0]
            state_moore_equal_mealy_transitions = []

            for transition_mealy_from_state in self.mealy_machine_data[state_mealy_equal_moore]:
                state_moore_equal_mealy_transitions.append(states_mealy_equal_moore[transition_mealy_from_state])

            moore_machine_data[state_moore].append(state_moore_equal_mealy_transitions)
            moore_machine_data[state_moore].append(out_signals[states_moore.index(state_moore)])

        return moore_machine_data

    def serialize_mealy_machine(self, mealy_machine_json_filepath: str = 'mealy_machine.json'):
        mealy_machine_json_data = json.dumps(self.mealy_machine_data)
        with open(mealy_machine_json_filepath, 'w') as mealy_json_file:
            mealy_json_file.write(mealy_machine_json_data)

    def draw_mealy_machine(self):
        G = nx.DiGraph(directed=True)
        net = Network(directed=True)

        G.add_nodes_from(self.mealy_machine_data.keys())

        state_transition_pairs = []
        state_transition_pairs_with_input_output_signals = {}
        for state, transitions in self.mealy_machine_data.items():
            for i in range(len(transitions)):
                state_transition_pairs.append((state, transitions[i].split('/')[0]))
                state_transition_pairs_with_input_output_signals[state_transition_pairs[-1]] = f"x{i + 1}/{transitions[i].split('/')[1]}"

        G.add_edges_from(state_transition_pairs)

        pos = nx.circular_layout(G)
        nx.draw(G, pos, with_labels=True)
        nx.draw_networkx_edge_labels(
            G, pos,
            edge_labels=state_transition_pairs_with_input_output_signals,
            font_color='red'
        )
        net.from_nx(G)
        net.show(name="graph.html")
