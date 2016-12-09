from numpy.random import normal, chisquare
from random import randint, random
from math import ceil

from cards.models import *
from cards.lib.agents.card_creator_agent import CardCreatorAgent

def generate_card(mana):
    creator = CardCreatorAgent()
    card = None
    while not card or card['mana'] != mana:
        card = creator.act()
    return card
