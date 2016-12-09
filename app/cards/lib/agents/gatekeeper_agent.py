import random
import re
from .evaluator import Evaluator

class Gatekeeper:

    def __init__(self, card_generators, n_insipiring_set):
        self._memory = []
        self._card_generators = card_generators
        self.evaluator = Evaluator(n_insipiring_set)


    # Mana 0+
    # HP 1+
    # Att 0+
    # Mechanic values 1+
    # Card value mana+-1
    def is_fair(self, card):
        # use simplevalue, mana, attack, health, card_mechanics
        if card['mana'] < 0:
            return False

        if card['attack'] < 0:
            return False

        if card['health'] < 1:
            return False

        if (abs(card['mana'] - card['value']) > 1):
            return False

        for mech in card['mechanics']:
            if any(char.isdigit() for char in mech[0]):
                digits = [int(s) for s in re.findall(r'\d+', mech[0])]
                for digit in digits:
                    if digit < 1:
                        return False

        #return self.evaluator.evaluate(card)
        return True

    # Novelty:
    # shouldn't be exactly the same as something in inspiring set, one of the following must differ:
    # mana
    # attack
    # health
    # card_mechanics
    def is_novel(self, card):
        filtered = [k for k in self._memory if k['mana'] == card['mana']]
        filtered = [k for k in filtered if k['attack'] == card['attack']]
        filtered = [k for k in filtered if k['health'] == card['health']]
        if not filtered:
            return True
        if card['mechanics']:
            for k in filtered:
                if (k['mechanics'] and (set(k['mechanics']) == set(card['mechanics']))):
                    return False
        return True

    def remember(self, card):
        self._memory.append(card)

    def act(self):
        artifacts = []
        while not artifacts:
            artifacts = [agent.act() for agent in self._card_generators]
            artifacts = [a for a in artifacts if self.is_fair(a) and self.is_novel(a)]
        (self.remember(a) for a in artifacts)
        return random.choice(artifacts)
