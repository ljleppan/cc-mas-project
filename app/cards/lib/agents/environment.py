from random import choice

from .card_creator_agent import CardCreatorAgent
from .gatekeeper_agent import Gatekeeper
from .deck_creator_agent import DeckCreatorAgent

class Environment:

    def __init__(self, n_card_creators, n_gatekeepers, n_deck_creators):
        self._deck_creators = []
        for _ in range(n_deck_creators):
            gatekeepers = []
            for _ in range(n_gatekeepers):
                card_creators = [CardCreatorAgent() for _ in range(n_card_creators)]
                gatekeeper = Gatekeeper(card_creators, 100)
                gatekeepers.append(gatekeeper)
            self._deck_creators.append(DeckCreatorAgent(gatekeepers, None))

    def step(self):
        return choice(self._deck_creators).act()
