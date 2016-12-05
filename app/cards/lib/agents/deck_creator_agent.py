import operator

class DeckCreatorAgent:

    def __init__(self, gatekeepers, evaluator):
        self._gatekeepers = gatekeepers
        self._evaluator = evaluator

    def act(self):
        deck = []
        for _ in range(30):
            choices = [agent.act() for agent in self._gatekeepers]
            choices = [(a, self._evaluator.evaluate(c)) for c in choices]
            choices.sort(key=operator.itemgetter(1))
            deck.append(choices[0][0])
        return deck
