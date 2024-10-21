import json
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network


class MealyMachine:
    def __init__(self, mealy_machine_data):  # Создание объекта из словаря типа {state: [transitions, out_signal]}
        self.mealy_machine_data = mealy_machine_data

    def __str__(self):
        col_width = max(len(state) for state in self.mealy_machine_data.keys()) + 2
        trans_width = (max(len(transition) for transitions in self.mealy_machine_data.values()
                           for transition in transitions) + 2)

        input_symbols = [f'x{i + 1}' for i in range(len(next(iter(self.mealy_machine_data.values()))))]
        header = "State".ljust(col_width) + ''.join(input_symbol.center(trans_width) for input_symbol in input_symbols)
        table = header + "\n" + "-" * len(header) + "\n"

        for state, transitions in self.mealy_machine_data.items():
            row = state.ljust(col_width)
            row += ''.join(transition.center(trans_width) for transition in transitions)
            table += row + "\n"

        return table

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

    def minimize_mealy_machine(self):
        partition = []
        for state, transitions in self.mealy_machine_data.items():
            output_signals = tuple(transition.split('/')[1] for transition in transitions)
            partition.append((state, output_signals))

        groups = {}
        for state, outputs in partition:
            if outputs not in groups:
                groups[outputs] = []
            groups[outputs].append(state)

        partition = list(groups.values())

        minimized = False
        while not minimized:
            minimized = True
            new_partition = []

            for group in partition:
                subgroups = {}

                for state in group:
                    signature = tuple(
                        next((i for i, group in enumerate(partition) if transition.split('/')[0] in group), -1)
                        for transition in self.mealy_machine_data[state]
                    )

                    if signature not in subgroups:
                        subgroups[signature] = []
                    subgroups[signature].append(state)

                if len(subgroups) > 1:
                    minimized = False

                new_partition.extend(subgroups.values())
            partition = new_partition

        state_mapping = {state: f's{index}' for index, group in enumerate(partition) for state in group}
        minimized_machine = {}

        for group in partition:
            representative = group[0]
            new_transitions = []

            for transition in self.mealy_machine_data[representative]:
                next_state, output_signal = transition.split('/')
                new_transitions.append(f"{state_mapping[next_state]}/{output_signal}")

            minimized_machine[state_mapping[representative]] = new_transitions

        return minimized_machine

    def draw_mealy_machine(self, output_filename: str):
        state_transition_pairs = []
        state_transition_pairs_with_input_output_signals = {}

        # Создание списка состояний и переходов
        for state, transitions in self.mealy_machine_data.items():
            for i in range(len(transitions)):
                # Получаем целевое состояние и выход
                target_state = transitions[i].split('/')[0]
                output_signal = transitions[i].split('/')[1]

                # Сохраняем пары состояний и переходы
                state_transition_pairs.append((state, target_state))
                state_transition_pairs_with_input_output_signals[
                    state_transition_pairs[-1]] = f"x{i + 1}/{output_signal}"

        # Создание объекта Pyvis Network
        net = Network(directed=True)

        # Добавляем узлы
        for state in self.mealy_machine_data.keys():
            net.add_node(state, label=state)

        # Добавляем ребра с метками (входы и выходы)
        for (src, dst) in state_transition_pairs:
            label = state_transition_pairs_with_input_output_signals[(src, dst)]
            net.add_edge(src, dst, label=label)

        # Настройка и сохранение графа
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

        # Сохраняем граф в HTML файл
        net.save_graph(output_filename)
