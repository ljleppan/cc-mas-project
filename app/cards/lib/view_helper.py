from cards.lib.agents.card_creator_agent import CardCreatorAgent
from cards.lib.agents.environment import Environment

def generate_card(mana):
    creator = CardCreatorAgent()
    card = None
    while not card or card['mana'] != mana:
        card = creator.act()
    return card


def generate_deck(style):
    env = Environment(10, 5, [style])
    deck = env.step()
    print("Created {} deck".format(style))
    return deck
