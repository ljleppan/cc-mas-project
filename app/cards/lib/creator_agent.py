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

        card['type'] = "Minion"
        card['mana'] = 3
        card['mechanics'] = [("Shit mechanic", 123)]
        card['health'] = 1
        card['attack'] = 2
        
        card['name'] = "Teemo's Mushroom"
        card['rarity'] = "Epic" #Rarity.objects.order_by('?').first().name
        card['race'] = "None"
        
        card['player_class'] = "All"
        
        card['value'] = -100
        card['image'] = "http://i.imgur.com/TqFP5w7.jpg"
        
        return card


if __name__ == "__main__":
    main()
