from random import choice

from cards.lib.agents.card_creator_agent import CardCreatorAgent
from cards.lib.agents.gatekeeper_agent import Gatekeeper
from cards.lib.agents.deck_creator_agent import DeckCreatorAgent

class Environment:
    """
    Represents a collection of agents, working together to produce decks of
    cards.
    """

    def __init__(self, n_card_creators, n_gatekeepers, n_deck_creators):
        """
        Creates a new :class:`.Environment` containing a set of agents.

        :param n_card_creators: Number of :class:`.CardCreatorAgent` each :class:`.Gatekeeper` is associated with.
        :param n_gatekeepers: Number of :class:`.Gatekeeper` each :class:`.DeckCreatorAgent` is associated with.
        :param n_deck_creators: Number of :class:`.DeckCreatorAgent` in this :class:`.Environment`.
        """

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
        """:return: List of all :class:`.CardCreatorAgent` in this :class:`.Environment`"""
        return self._card_creators

    @property
    def gatekeepers(self):
        """:return: List of all :class:`.Gatekeeper` in this :class:`.Environment`"""
        return self._gatekeepers

    @property
    def deck_creators(self):
        """:return: List of all :class:`.DeckCreatorAgent` in this :class:`.Environment`"""
        return self._deck_creators

    def step(self):
        """
        Runs the simulation for one step, producing a new deck.

        The deck creator that finally produces the deck is at this point chosen
        randomly from among all the deck creators.

        :return: A list of 30 dicts, each dict presenting a card
        """
        return choice(self._deck_creators).act()
