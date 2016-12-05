from numpy.random import normal
from scipy.stats import truncnorm
from math import ceil

from cards.models import *


def main():
    print("Test")
    creator = Cretor_agent()
    card = creator.create_card()
    print(card)

class Creator_agent:
    def __init__(self):
        pass
    
    def create_card(self):
        card = {}
        card_val = 0

        
        card['mana'] = int(round(normal(2.5, 1.5)))
        card['mechanics'] = [("Shit mechanic", 123)]
        
        card_val += self._set_healt_and_attack(card, card["mana"])
        
        card['name'] = "Teemo's Mushroom"
        card['rarity'] = "Epic" #Rarity.objects.order_by('?').first().name
        card['race'] = "None"
        
        card['player_class'] = "All"
        
        
        card['image'] = "http://i.imgur.com/TqFP5w7.jpg"
        
        card['value'] = card_val
        card['type'] = "Minion"
        return card
    
    
    def _set_healt_and_attack(self, card, mana):
        '''Generates health and attack for a card based on given mana. Mana
        is divided for health and attack by using truncated normal
        distribution.

        :param dict card: card to set the values to
        :param int mana: total mana the values should be based on
        :returns:
            combined value of the attack and health generated
        '''
        
        #mana values for single attack and health points
        health_val = MetaData.objects.get(name='health_coeff').value
        attack_val = MetaData.objects.get(name='minion_attack_coeff').value
        print(health_val)
        print(attack_val)
        
        #random value between 0 and 1 using truncated normal distribution
        #with mean 0.5 and standard deviation 0.2
        rnd = truncnorm(-0.5/0.2, 0.5/0.2, loc=0.5, scale=0.2).rvs()
        
        health_val_target = rnd * mana
        attack_val_target = (1 - rnd) * mana
        print(health_val_target)
        print(attack_val_target)
        
        card['health'] = int(round(health_val_target/health_val))
        card['attack'] = int(round(attack_val_target/attack_val))
        
        return card['health'] * health_val + card['attack'] * attack_val


if __name__ == "__main__":
    main()
