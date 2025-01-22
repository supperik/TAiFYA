import re
from pyvis.network import Network


class NFA:
    def __init__(self, states, inputs, transitions, start_state):
        self.states = states
        self.inputs = inputs
        self.transitions = transitions
        self.start_state = start_state

    @classmethod
    def from_grammar(cls, grammar):
        states = list()  # Список состояний
        inputs = set()  # Входные символы
        transitions = {}  # Переходы
        final_state = 'H'  # Конечное состояние для праволинейной грамматики
        is_left = False  # Определяем тип грамматики

        for grammar_line in grammar:
            grammar_line = grammar_line.strip()
            if not grammar_line or '->' not in grammar_line:
                continue

            # Определяем тип грамматики
            if re.search(r'<[^>]+>\s*->\s*<[^>]+>[^\s|]+', grammar_line):
                is_left = True

            # Парсим правило
            lhs, rhs = map(str.strip, grammar_line.split('->'))
            current_state = re.match(r'<([^>]+)>', lhs).group(1)
            states.append(current_state)

            for production in rhs.split('|'):
                production = production.strip()
                match = re.fullmatch(r'<([^>]+)>(.+)?', production) \
                    if is_left else re.fullmatch(r'(.+)<([^>]+)>', production)
                if match:
                    if is_left:
                        # Леволинейная грамматика
                        next_state, symbol = match.groups()
                        symbol = symbol or ''  # Если символа нет, это ε-переход
                        inputs.add(symbol)
                        transitions.setdefault((next_state, symbol), set()).add(current_state)
                    else:
                        # Праволинейная грамматика
                        symbol, next_state = match.groups()
                        symbol = symbol or ''  # Если символа нет, это ε-переход
                        inputs.add(symbol)
                        transitions.setdefault((current_state, symbol), set()).add(next_state)
                else:
                    # Переходы в конечное или начальное состояние
                    match = re.fullmatch(r'[^\s|]+', production)
                    if match:
                        symbol = match.group(0)
                        inputs.add(symbol)
                        if is_left:
                            transitions.setdefault((final_state, symbol), set()).add(current_state)
                        else:
                            transitions.setdefault((current_state, symbol), set()).add(final_state)

        states.append(final_state)

        start_state = final_state if is_left else states[0]

        return cls(states=list(states), inputs=list(inputs), transitions=transitions, start_state=start_state)

    @classmethod
    def from_grammar_file(cls, filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            grammar = file.readlines()
        return cls.from_grammar(grammar)

    @classmethod
    def from_file(cls, filename: str):
        with open(filename, "r") as in_file:
            lines = in_file.readlines()

            states = [item.rstrip() for item in lines[0].split(';')[1:]]
            start_state = states[0]
            inputs = set()

            transitions = {}
            for line in lines[1:]:
                signal = line.split(';')[0].strip()
                inputs.add(signal)
                for i, transition in enumerate(line.split(';')[1:]):
                    if transition.strip() != '-':
                        for item in transition.split(','):
                            item = item.strip()
                            transitions.setdefault((states[i], signal), set()).add(item)

        return cls(states, inputs, transitions, start_state)

    def to_table(self):
        header = [' '] + self.states  # Заголовок таблицы (состояния)
        rows = []
        temp_inputs = sorted(self.inputs)

        for input_symbol in temp_inputs:
            row = [input_symbol]  # Первая ячейка строки — входной символ
            for state in self.states:
                # Получаем множество переходов
                next_states = self.transitions.get((state, input_symbol), set())
                # Если переходов нет, заполняем '-'
                row.append(','.join(sorted(next_states)) if next_states else '-')
            rows.append(row)

            # Формируем таблицу как строку
        table = [header] + rows
        table_str = '\n'.join([';'.join(cell for cell in row) for row in table])
        return table_str

    def __str__(self):
        return self.to_table()

    def draw_nfa(self, output_filename):
        # Создаем объект для визуализации графа
        net = Network(directed=True)

        # Добавляем узлы для состояний
        for state in self.states:
            if state == self.start_state:  # Выделяем стартовое состояние, например, красным
                net.add_node(state, label=state, color="red")  # Цвет для стартового состояния
            else:
                net.add_node(state, label=state)

        # Добавляем рёбра (переходы) между состояниями
        for (src, symbol), dst_set in self.transitions.items():
            for dst in dst_set:
                net.add_edge(src, dst, label=symbol)  # Переход подписан символом

        # Дополнительные опции для улучшения визуализации
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

        # Сохраняем граф в файл
        net.save_graph(output_filename)
