import operator
import numpy as np
from random import choice
from cards.models import *

class DeckCreatorAgent:

    def __init__(self, env, gatekeepers, evaluator):
        self._env = env
        self._gatekeepers = gatekeepers
        self._evaluator = evaluator

    def act(self):
        deck = []
        for _ in range(30):
            choices = [agent.act() for agent in self._gatekeepers]
            print("DeckCreator: Received {} cards from gatekeepers: {}".format(len(choices), choices))
            choices = [(
                            c,
                            self._evaluator.evaluate(c) * (1 + self._evaluate_mana_curve(c, deck))
                        )
                        for c in choices]
            choices.sort(key=operator.itemgetter(1), reverse=True)
            winner = choices[0]
            deck.append(winner[0])
            print("DeckCreator: Determined best card at value={}: {}".format(winner[1], winner[0]))
            print("DeckCreator: Informing GateKeepers of winner")
            (agent.remember(card) for agent in self._env.gatekeepers)
        curve = [card['mana'] for card in deck]
        curve.sort()
        print("DeckCreator: Created deck with mana curve", curve)
        deck.sort(key=operator.itemgetter('mana'))
        return deck

    def _evaluate_mana_curve(self, card, previous_cards):
        curve = [card['mana'] for card in previous_cards]

        lows = 0
        meds = 0
        highs = 0
        for m in range(0, 5):
            lows += curve.count(m)
        for m in range(5, 8):
            meds += curve.count(m)
        for m in range(8, 11):
            highs += curve.count(m)

        target_highs = 5
        target_meds = 10
        target_lows = 15

        curve_fit = 0
        if card['mana'] in range(0, 5):
            curve_fit = 1 - (lows / target_lows)
        if card['mana'] in range(5, 8):
            curve_fit = 1 - (meds / target_meds)
        if card['mana'] in range(8, 11):
            curve_fit = 1 - (highs / target_highs)


        curve_weight = 5 * (len(curve) / 30)
        curve_fit *= curve_weight
        print("DeckCreator: Evaluated {} ({} mana) as fitting the mana curve worth {}, with curve weigth {}".format(card['name'], card['mana'], curve_fit, curve_weight))
        return curve_fit


class DefaultEvaluator:

    def evaluate(self, card):
        value = (card['attack'] + card['health']) / 2
        for mechanic, id, effectsize in card['mechanics']:
            db_mechanic = Mechanic.objects.get(pk=id)
            mechanic_value = db_mechanic.value * effectsize
            mechanic_value = round(mechanic_value * 2) / 2 # Round to nearest 0.5
            value += mechanic_value
        print("DeckCreator: Card quality of {}: {}".format(card['name'], value))
        return value

class DefensiveEvaluator:

    def evaluate(self, card):
        value = ((card['attack'] * 0.75) + (card['health']*1.25)) / 2
        for mechanic, id, effectsize in card['mechanics']:
            db_mechanic = Mechanic.objects.get(pk=id)
            mechanic_value = db_mechanic.value * effectsize
            mechanic_value = round(mechanic_value * 2) / 2 # Round to nearest 0.5
            value += mechanic_value
            if "taunt" in db_mechanic.name.lower() or "heal" in db_mechanic.name.lower():
                if db_mechanic.value > 0:
                    print("DeckCreator: Overvaluing positive taunt or heal")
                    mechanic_value += 0.25
            value += mechanic_value
        print("DeckCreator: Card quality of {}: {}".format(card['name'], value))
        return value

class OffensiveEvaluator:

    def evaluate(self, card):
        value = ((card['attack'] * 1.25) + (card['health']*0.75)) / 2
        for mechanic, id, effectsize in card['mechanics']:
            db_mechanic = Mechanic.objects.get(pk=id)
            mechanic_value = db_mechanic.value * effectsize
            mechanic_value = round(mechanic_value * 2) / 2 # Round to nearest 0.5
            value += mechanic_value
            if "windfury" in db_mechanic.name.lower() or "damage" in db_mechanic.name.lower():
                if db_mechanic.value > 0:
                    print("DeckCreator: Overvaluing windfury or damage")
                    mechanic_value += 0.25
            if "can't attack" in db_mechanic.name.lower():
                print("DeckCreator: Undervauing ''can't attack''")
                mechanic_value -= 0.25
            value += mechanic_value
        print("DeckCreator: Card quality of {}: {}".format(card['name'], value))
        return value
