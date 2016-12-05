import random

class Gatekeeper:

    self._memory = []

    def __init__(self, card_generators):
        self._card_generators = card_generators

    def is_fair(self, card):
        return True

    def is_novel(self, card):
        return True

    def remember(self, card)
        self._memory.append(card)

    def act(self):
        artifacts = [agent.act() for agent in self._card_generators]
        artifacts = [a for a in artifacts if self.is_fair(a) and self.is_novel(a)]
        (self.remember(a) for a in artifacts)
        return random.choice(self._memory)
