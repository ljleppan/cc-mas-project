## Testing git pushes before making real changes

import operator
from random import choice

class DeckCreatorAgent:

    def __init__(self, gatekeepers, evaluator):
        self._gatekeepers = gatekeepers
        self._evaluator = evaluator

    def act(self):
        deck = []
        for _ in range(30):
            choices = [agent.act() for agent in self._gatekeepers]
            if self._evaluator:
                choices = [(c, self._evaluator.evaluate(c)) for c in choices]
                choices.sort(key=operator.itemgetter(1))
                deck.append(choices[0][0])
            else:
                deck.append(choice(choices))
        return deck
