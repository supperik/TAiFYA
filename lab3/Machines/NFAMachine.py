import re
from pyvis.network import Network


class NFA:
    def __init__(self, states, inputs, transitions, start_state, accept_states):
        self.states = states  # Все состояния NFA
        self.inputs = inputs  # Алфавит NFA
        self.transitions = transitions  # Таблица переходов NFA
        self.start_state = start_state  # Начальное состояние
        self.accept_states = accept_states  #self._find_accept_states()  # Автоматически определяем конечные состояния

    def _find_accept_states(self):
        """
        Определяет принимающие состояния:
        Состояния, из которых возможен ε-переход в конечное состояние или пустое множество.
        """
        accept_states = set()
        for state in self.states:
            if (state, '') in self.transitions:  # Проверяем наличие ε-перехода
                reachable_states = self.transitions[(state, '')]
                if not reachable_states:  # Если ε-переход ведёт в пустое множество
                    accept_states.add(state)
        return accept_states

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
        with open(filename, "r", encoding="utf-8") as in_file:
            lines = in_file.readlines()

            # Парсим состояния
            outputs = [item.rstrip() for item in lines[0].split(';')[1:]]
            states = [item.rstrip() for item in lines[1].split(';')[1:]]
            start_state = states[0]

            # Парсим входные символы
            inputs = set()

            # Парсим переходы
            transitions = {}
            accept_states = []
            for line in lines[2:]:
                signal = line.split(';')[0].strip()
                inputs.add(signal)
                for i, transition in enumerate(line.split(';')[1:]):
                    if transition.strip() != '-':
                        for item in transition.split(','):
                            item = item.strip()
                            if item != '':
                                transitions.setdefault((states[i], signal), set()).add(item)

            for i in range(len(outputs)):
                if outputs[i] == 'F':
                    accept_states.append(states[i])
        return cls(states, inputs, transitions, start_state, accept_states)

    def to_table(self):
        header = [''] + self.states  # Заголовок таблицы (состояния)
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
            # print(state)
            if state == self.start_state:  # Выделяем стартовое состояние, например, красным
                net.add_node(state, label=state, color="red")  # Цвет для стартового состояния
            else:
                net.add_node(state, label=state)

        # Добавляем рёбра (переходы) между состояниями
        for (src, symbol), dst_set in self.transitions.items():
            for dst in dst_set:
                # print()
                net.add_edge(src, dst, label=symbol)  # Переход подписан символом

        # Дополнительные опции для улучшения визуализации
        net.set_options("""
                        var options = {
                            "edges": {
                                "color": {
                                    "inherit": true
                                }
                            }
                        }
                    """)

        # Сохраняем граф в файл
        net.save_graph(output_filename)
