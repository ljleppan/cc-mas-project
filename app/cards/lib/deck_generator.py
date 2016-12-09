from numpy.random import normal, chisquare
from random import randint, random
from math import ceil

from cards.models import *
from cards.lib.agents.card_creator_agent import CardCreatorAgent

def generate_deck(style):
    agent = CardCreatorAgent()
    return [agent.act() for _ in range(30)]
