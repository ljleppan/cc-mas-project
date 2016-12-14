from random import choice

from cards.lib.agents.card_creator_agent import CardCreatorAgent
from cards.lib.agents.gatekeeper_agent import Gatekeeper
from cards.lib.agents.deck_creator_agent import DeckCreatorAgent, DefaultEvaluator, OffensiveEvaluator, DefensiveEvaluator

class Environment:
    """
    Represents a collection of agents, working together to produce decks of
    cards.
    """

    def __init__(self, n_card_creators, n_gatekeepers, deck_creator_styles):
        """
        Creates a new :class:`.Environment` containing a set of agents.

        :param n_card_creators: Number of :class:`.CardCreatorAgent` each :class:`.Gatekeeper` is associated with.
        :param n_gatekeepers: Number of :class:`.Gatekeeper` each :class:`.DeckCreatorAgent` is associated with.
        :param deck_creator_styles: Styles of :class:`.DeckCreatorAgent` instances in this :class:`.Environment`.
        """

        self._card_creators = []
        self._gatekeepers = []
        self._deck_creators = []

        deck_creator_evaluators = {
            None: DefaultEvaluator(),
            "standard": DefaultEvaluator(),
            "offensive": OffensiveEvaluator(),
            "defensive": DefensiveEvaluator()
        }

        for style in deck_creator_styles:
            gatekeepers = []
            for _ in range(n_gatekeepers):
                card_creators = [CardCreatorAgent() for _ in range(n_card_creators)]
                self._card_creators.extend(card_creators)
                gatekeeper = Gatekeeper(self, card_creators, 200)
                gatekeepers.append(gatekeeper)
                self._gatekeepers.append(gatekeeper)
            self._deck_creators.append(DeckCreatorAgent(self, gatekeepers, deck_creator_evaluators[style]))

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
