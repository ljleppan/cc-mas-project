from random import choice

from cards.lib.agents.card_creator_agent import CardCreatorAgent
from cards.lib.agents.gatekeeper_agent import Gatekeeper
from cards.lib.agents.deck_creator_agent import DeckCreatorAgent

class Environment:

    def __init__(self, n_card_creators, n_gatekeepers, n_deck_creators):
        self._card_creators = []
        self._gatekeepers = []
        self._deck_creators = []

        for _ in range(n_deck_creators):
            gatekeepers = []
            for _ in range(n_gatekeepers):
                card_creators = [CardCreatorAgent() for _ in range(n_card_creators)]
                self._card_creators.extend(card_creators)
                gatekeeper = Gatekeeper(self, card_creators, 200)
                gatekeepers.append(gatekeeper)
                self._gatekeepers.append(gatekeeper)
            self._deck_creators.append(DeckCreatorAgent(gatekeepers, None))

    @property
    def card_creators(self):
        return self._card_creators

    @property
    def gatekeepers(self):
        return self._gatekeepers

    @property
    def deck_creators(self):
        return self._deck_creators

    def step(self):
        return choice(self._deck_creators).act()
