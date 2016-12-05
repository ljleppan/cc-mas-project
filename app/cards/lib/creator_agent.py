from numpy.random import normal, random_integers, poisson
import numpy as np
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
        
        card_val += self._generate_mechanics(card)
        card_val += self._generate_health_and_attack(card, card["mana"] - card_val)
        
        
        card['name'] = "Teemo's Mushroom"
        card['race'] = "None"
        
        card['player_class'] = "All"
        
        
        card['image'] = "http://i.imgur.com/TqFP5w7.jpg"
        
        card['value'] = card_val
        self._define_rarity(card)
        card['type'] = "Minion"
        return card
        
    def _define_rarity(self, card):
        '''Sets the rarity of the card based on it's manacost and value.

        :param dict card: card to set the rarity to
        '''
        #r = list(Rarity.objects.all())
        #print(r)
        diff = card["value"] - card["mana"]
        
        if diff < 0.1:
            card["rarity"] = "Common"
        elif diff < 0.2:
            card["rarity"] = "Rare"
        elif diff < 0.3:
            card["rarity"] = "Epic"
        else:
            card["rarity"] = "Legendary"
        
        
    def _generate_mechanics(self, card, max_mechanics=5):
        mechanics = list(Mechanic.objects.all().filter(cardmechanic__card__cardType__name__exact="Minion").order_by('value'))
        
        
        total_value = 0
        chosen = []
        
        for i in range(min(poisson(2), max_mechanics)):
            mech = mechanics[random_integers(len(mechanics))]
            
            if "%d" in mech.name:
                d = poisson(2)
                chosen.append((mech.name.replace("%d", str(d)), mech.id))
                total_value += (mech.value * d)
            else:
                chosen.append((mech.name, mech.id))
                total_value += mech.value
        
        print(chosen)
        
        card['mechanics'] = chosen
        return total_value
        
    def _generate_mechanics_baaad(self, card, mana, max_mechanics=5):
        mechanics = np.array(list(Mechanic.objects.all().filter(cardmechanic__card__cardType__name__exact="Minion").order_by('value')))
        mechanics_values = np.array([mech.value for mech in mechanics])
        mechanics_neg = mechanics[mechanics_values < 0.0]
        mechanics_neu = mechanics[mechanics_values == 0.0]
        mechanics_pos = mechanics[mechanics_values > 0.0]
        print(len(mechanics_neg))
        print(len(mechanics_neu))
        print(len(mechanics_pos))
        total_value = 0
        chosen = []
        
        if abs(mana) > 0.2:
            while len(chosen) < max_mechanics and abs(total_value - mana) > 0.2:
                mech = None
                if mana -total_value > 0:
                    mech = mechanics_pos[random_integers(len(mechanics_pos))]
                else:
                    mech = mechanics_neg[random_integers(len(mechanics_neg))]
                chosen.append((mech.name, mech.id))
                total_value += mech.value
        
        print(chosen)
        
        card['mechanics'] = chosen
        return total_value
    
    def _generate_health_and_attack(self, card, mana):
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
        #print(health_val)
        #print(attack_val)
        
        #random value between 0 and 1 using truncated normal distribution
        #with mean 0.5 and standard deviation 0.2
        rnd = truncnorm(-0.5/0.2, 0.5/0.2, loc=0.5, scale=0.2).rvs()
        
        health_val_target = rnd * mana
        attack_val_target = (1 - rnd) * mana
        #print(health_val_target)
        #print(attack_val_target)
        
        card['health'] = int(round(health_val_target/health_val))
        card['attack'] = int(round(attack_val_target/attack_val))
        
        return card['health'] * health_val + card['attack'] * attack_val


if __name__ == "__main__":
    main()
