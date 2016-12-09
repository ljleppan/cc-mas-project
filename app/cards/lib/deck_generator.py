from numpy.random import normal, chisquare
from random import randint, random
from math import ceil

from cards.models import *
from cards.lib.agents.environment import Environment

def generate_deck(style):
    env = Environment(5, 3, 1)
    return env.step()
