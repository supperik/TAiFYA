from pyvis.network import Network
from collections import defaultdict


def load_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read().strip()


def save_to_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def process_input(data):
    lines = data.splitlines()
    outputs = lines[0].split(';')[1:]
    nodes = lines[1].split(';')[1:]
    transitions_map = {}
    for line in lines[2:]:
        label, *transitions = line.split(';')
        transitions_map[label] = transitions

    return outputs, nodes, transitions_map


def compute_closure(state, transitions, nodes):
    closure_set = {state}
    stack = [state]
    while stack:
        current_node = stack.pop()
        state_index = nodes.index(current_node)
        if transitions[0][state_index] == '-':  # Отсутствие ε-перехода
            continue
        next_state = transitions[0][state_index]
        if next_state not in closure_set:
            closure_set.add(next_state)
            stack.append(next_state)
    return closure_set


def generate_all_closures(nodes, transitions):
    closures_dict = {}
    for node in nodes:
        closures_dict[node] = compute_closure(node, transitions, nodes)
    return closures_dict


def minimize_machine(outputs, nodes, transitions):
    partitions = defaultdict(list)
    for idx, node in enumerate(nodes):
        partitions[outputs[idx]].append(node)

    groups = list(partitions.values())
    while True:
        updated_groups = []
        for cluster in groups:
            new_groups = defaultdict(list)
            for node in cluster:
                key = tuple(
                    find_group_index(groups, transitions[i][nodes.index(node)])
                    for i in transitions
                )
                new_groups[key].append(node)
            updated_groups.extend(new_groups.values())

        if len(updated_groups) == len(groups):
            break
        groups = updated_groups

    reduced_nodes = ['q' + str(i) for i in range(len(groups))]
    mapping = {node: 'q' + str(i) for i, cluster in enumerate(groups) for node in cluster}

    reduced_transitions = {}
    for label in transitions:
        reduced_transitions[label] = []
        for cluster in groups:
            target_node = transitions[label][nodes.index(cluster[0])]
            reduced_transitions[label].append(mapping.get(target_node, '-'))

    reduced_outputs = [outputs[nodes.index(group[0])] for group in groups]
    return reduced_outputs, reduced_nodes, reduced_transitions


def find_group_index(groups, node):
    for idx, group in enumerate(groups):
        if node in group:
            return idx
    return -1


def remove_unused_states(outputs, nodes, transitions, start='q0'):
    reachable_nodes = set()
    to_visit = [start]

    while to_visit:
        current = to_visit.pop()
        if current not in reachable_nodes:
            reachable_nodes.add(current)
            node_index = nodes.index(current)
            for transition in transitions:
                next_node = transitions[transition][node_index]
                if next_node != '-' and next_node not in reachable_nodes:
                    to_visit.append(next_node)

    indices = [nodes.index(node) for node in reachable_nodes]
    cleaned_outputs = [outputs[i] for i in indices]
    cleaned_nodes = list(reachable_nodes)
    cleaned_transitions = {label: [transitions[label][i] for i in indices] for label in transitions}

    return cleaned_outputs, cleaned_nodes, cleaned_transitions


def create_output_string(minimized_outputs, minimized_nodes, minimized_transitions):
    result = ';' + ';'.join(minimized_outputs) + '\n'
    result += ';' + ';'.join(minimized_nodes) + '\n'
    for idx, (label, transition) in enumerate(minimized_transitions.items()):
        result += f'x{idx + 1};' + ';'.join(transition) + '\n'
    return result


def draw_graph(outputs, nodes, transitions, filename):
    graph = Network(directed=True, notebook=False)
    for node in nodes:
        if outputs[nodes.index(node)] == 'F':
            graph.add_node(node, label=node, title=node, color="red")
        else:
            graph.add_node(node, label=node, title=node)

    for label, transition in transitions.items():
        for src, dst in zip(nodes, transition):
            if dst != '-':
                graph.add_edge(src, dst, label=label)

    graph.set_options("""
                var options = {
                    "edges": {
                        "color": {
                            "inherit": true
                        },
                        "smooth": false
                    }
                }
            """)

    graph.save_graph(filename)


input_data = load_file('minim_in.txt')
outputs, nodes, transitions = process_input(input_data)

transition_values = list(transitions.values())

closures = generate_all_closures(nodes, transition_values)

simplified_outputs, simplified_nodes, simplified_transitions = minimize_machine(outputs, nodes, transitions)

final_outputs, final_nodes, final_transitions = remove_unused_states(
    simplified_outputs, simplified_nodes, simplified_transitions
)

result_str = create_output_string(final_outputs, final_nodes, final_transitions)
save_to_file('minim_out.txt', result_str)

draw_graph(final_outputs, final_nodes, final_transitions, "minimized_graph.html")
