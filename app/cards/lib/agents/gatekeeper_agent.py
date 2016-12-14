from random import choice
import re
import numpy as np
from sklearn.linear_model import Ridge
from cards.models import *
from cards.lib.agents.limited_memory import LimitedMemory
from cards.lib.agents.learning_utils import data_as_numpy_array, card_as_row

class Gatekeeper:
    """
    A gatekeeper agent. Each :class:`.Gatekeeper` knows a certain set of :class:`.CardCreatorAgent`
    instances. It can also talk to other :class:`.Gatekeeper` instances through :class:`.Environment`.

    Each :class:`.Gatekeeper` has a static inspiring set of real cards it uses
    to evalute the fairness of new cards, as well as a limited memory of previously
    seen generated cards that it uses to evaluate novelty.
    """

    def __init__(self, env, card_generators, subset_size):
        """
        Creates a new :class:`.Gatekeeper` agent.

        :param env: The :class:`.Environment` this :class:`.Gatekeeper` lives in.
        :param card_generators: A list of all :class:`.CardCreatorAgent` instances this :class:`.Gatekeeper` is associated with.
        :param subset_size: The size of inspiring set this :class:`.Gatekeeper` has.
        """
        self._env = env
        self._memory = LimitedMemory(100)
        self._card_generators = card_generators
        self._load_card_subset(subset_size)
        self._learn_coeffs()

    def _load_card_subset(self, subset_size):
        print("Gatekeeper: Learning to evaluate card values for a random subset of size", str(subset_size))

        try:
            data = np.load("heathstonedata.npy")
            print("Gatekeeper: Loaded card data from cache")
        except Exception:
            print("Gatekeeper: Did not find cached data, reading from DB (This WILL take ~10 minutes)")
            data =  data_as_numpy_array()
            print("Gatekeeper: Loading complete, caching data")
            np.save("heathstonedata.npy", data)
            print("Gatekeeper: Caching complete")

        sub_indices = np.random.choice(max(len(data), subset_size), subset_size)
        self._cards = np.ascontiguousarray(data[:, 1:][sub_indices], dtype=np.float)


    def _learn_coeffs(self):
        y = np.ascontiguousarray(self._cards[:, 0], dtype=np.float)
        X = np.ascontiguousarray(self._cards[:, 1:], dtype=np.float)

        print("Learning coefficients (gatekeeper agent).")
        self._model = Ridge(alpha=0.00001)
        self._model.fit(X, y)

        print("Learning complete.")
        print("\tAccuracy: {}".format(self._model.score(X, y)))


    def is_fair(self, card):
        """
        Determines whether the inpur card is "fair" or not.

        Fair cards have non-negative mana and attack value and a positive health.

        Similarly, all mechanics with effect sizes ("X" in "Deal X damage") must
        have positive effect sizes, and no duplicate mechanics are allowed within
        a single card.

        Finally, card value (as estimated by a model fit on the inspiring set of
        this :class:`.Gatekeeper`) must be within 1 of the card's mana cost.

        :param card: Card to evaluate.

        :return: `True` if card is fair, `False` otherwise.
        """
        if card['mana'] < 0:
            #print("Gatekeeper: Discarding card with < 0 mana")
            return False

        if card['attack'] < 0:
            #print("Gatekeeper: Discarding card with < 0 attack")
            return False

        if card['health'] < 1:
            #print("Gatekeeper: Discarding card with < 1 attack")
            return False

        for mech in card['mechanics']:
            if any(char.isdigit() for char in mech[0]):
                digits = [int(s) for s in re.findall(r'\d+', mech[0])]
                for digit in digits:
                    if digit < 1:
                        #print("Gatekeeper: Discarding card with mechanic value < 1")
                        return False

        # Remove cards with duplicate mechanics
        mechanics = [x[1] for x in card['mechanics']]
        if len(mechanics) != len(set(mechanics)):
            #print("Gatekeeper: Discarding card with duplicate mechanics")
            return False

        np_card = card_as_row(card)
        evaluation = self._model.predict(np_card)
        value_delta = card['mana'] - evaluation
        #print("Gatekeeper: evaluated card as {}. Delta: {}".format(evaluation, value_delta))
        if (abs(value_delta) > 1):
            return False

        return True

    def is_novel(self, card):
        """
        Determines whether an input card is novel.

        A card is *not* novel if it shares a name with a memorized card, or it
        has the exact same combination of mana, health, attack and mechanics as
        another card in memory.

        :param card: Card to evaluate.

        :return: `True` if the card is novel, `False` otherwise.
        """
        filtered = [k for k in self._memory.items if k['mana'] == card['mana']]
        filtered = [k for k in filtered if k['attack'] == card['attack']]
        filtered = [k for k in filtered if k['health'] == card['health']]
        if not filtered:
            return True

        for k in filtered:
            if (card['name'] == k['name']):
                return False

        if card['mechanics']:
            for k in filtered:
                if (k['mechanics'] and (set(k['mechanics']) == set(card['mechanics']))):
                    #print("Gatekeeper: Discarding duplicate card")
                    return False

        return True


    def remember(self, card):
        """
        Add a new card to the limited memory of this :class:`.Gatekeeper`. If the
        memory is already full, the oldest card is purged from memory.

        :param card: Card to memorize.
        """
        print("Gatekeeper: Memorizing card and telling CardGenerators about it")
        self._memory.append(card)
        (agent.memoize(card) for agent in self._card_generators)


    def act(self):
        """
        Act one "round" of the simulation.

        The :class:`.Gatekeeper` asks each :class:`.CardCreatorAgent` to produce
        a new card. Any non-novel and non-fair cards are discarded. For the remaining
        cards, the opinion of one other :class:`.Gatekeeper` -- chosen randomly from
        the :class:`.Environment` -- is asked on whether the cards indeed are both
        fair and novel.

        If both this and the other :class:`.Gatekeeper` agreed on any cards, this
        :class:`.Gatekeeper` commits them all to memory and then randomly chooses
        one winner.

        The winner is then broadcasted to all other :class:`.Gatekeeper` instances
        so that they, too, remember it for future novelty checks.
        """
        artifacts = []
        while not artifacts:
            artifacts = [agent.act() for agent in self._card_generators]
            print("Gatekeeper: got {} cards from card creators".format(len(artifacts)))
            artifacts = [a for a in artifacts if self.is_fair(a) and self.is_novel(a)]
            print("Gatekeeper: {} cards were novel and fair".format(len(artifacts)))
            other_gatekeeper = choice(self._env.gatekeepers)
            artifacts = [a for a in artifacts if other_gatekeeper.is_fair(a) and other_gatekeeper.is_novel(a)]
            print("Gatekeeper: other gatekeeper agreed about {} cards".format(len(artifacts)))

        # Remember all fair and novel candidates
        (agent.remember(a) for a in artifacts)

        # Select winner
        winner = choice(artifacts)

        # Broadcast winner to all other gatekeepers
        (agent.remember(winner) for agent in self._env.gatekeepers)

        return winner
