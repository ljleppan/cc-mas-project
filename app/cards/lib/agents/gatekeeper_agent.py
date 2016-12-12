from random import choice
import re
import numpy as np
from sklearn.linear_model import Ridge
from cards.models import *
from .evaluator import Evaluator
from .limited_memory import LimitedMemory
from .learning_utils import data_as_numpy_array, card_as_row

class Gatekeeper:

    def __init__(self, env, card_generators, subset_size):
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
        if card['mana'] < 0:
            print("Gatekeeper: Discarding card with < 0 mana")
            return False

        if card['attack'] < 0:
            print("Gatekeeper: Discarding card with < 0 attack")
            return False

        if card['health'] < 1:
            print("Gatekeeper: Discarding card with < 1 attack")
            return False

        for mech in card['mechanics']:
            if any(char.isdigit() for char in mech[0]):
                digits = [int(s) for s in re.findall(r'\d+', mech[0])]
                for digit in digits:
                    if digit < 1:
                        print("Gatekeeper: Discarding card with mechanic value < 0")
                        return False

        # Remove cards with duplicate mechanics
        mechanics = [x[1] for x in card['mechanics']]
        if len(mechanics) != len(set(mechanics)):
            print("Gatekeeper: Discarding card with duplicate mechanics")
            return False

        np_card = card_as_row(card)
        evaluation = self._model.predict(np_card)
        value_delta = card['mana'] - evaluation
        print("Gatekeeper: evaluated card as {}. Delta: {}".format(evaluation, value_delta))
        if (abs(value_delta) > 1):
            return False

        return True

    def is_novel(self, card):
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
                    print("Gatekeeper: Discarding duplicate card")
                    return False

        return True


    def remember(self, card):
        self._memory.append(card)
        (agent.memoize(card) for agent in self._card_generators)


    def act(self):
        artifacts = []
        while not artifacts:
            artifacts = [agent.act() for agent in self._card_generators]
            artifacts = [a for a in artifacts if self.is_fair(a) and self.is_novel(a)]
            other_gatekeeper = choice(self._env.gatekeepers)
        (self.remember(a) for a in artifacts)
        return choice(artifacts)
