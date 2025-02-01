class State:
    """Класс для состояния НКА."""

    def __init__(self):
        self.transitions = {}
        self.epsilon_transitions = []