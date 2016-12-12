from cards.models import *
import numpy as np

def card_as_row(card):
    row = [
        card['health'],
        card['attack'],
        0,
        0,
    ]

    for ctype in CardType.objects.all().order_by('id'):
        if card['type'] == ctype.name:
            row.append(1)
        else:
            row.append(0)

    for race in Race.objects.all().order_by('id'):
        if card['race'] == race.name:
            row.append(1)
        else:
            row.append(0)

    for mechanic in Mechanic.objects.all().order_by('id'):
        if len(card['mechanics']) == 0:
            row.append(0)
        else:
            found = False
            for card_mechanic in card['mechanics']:
                if card_mechanic[1] == mechanic.id:
                    row.append(card_mechanic[2])
                    found = True
                    break
            if not found:
                row.append(0)

    return np.array(row).reshape(1, -1)

def data_as_numpy_array():
    data = []
    for card in Card.objects.all():
        item = [
            card,
            card.mana,
        ]

        if card.cardType.name == "Minion":
            item.extend([card.health, card.attack, 0, 0])
        elif card.cardType.name == "Weapon":
            item.extend([0, 0, card.health, card.attack])
        else:
            item.extend([0, 0, 0, 0])

        for ctype in CardType.objects.all().order_by('id'):
            if card.cardType.id == ctype.id:
                item.append(1)
            else:
                item.append(0)

        for race in Race.objects.all().order_by('id'):
            if card.race.id == race.id:
                item.append(1)
            else:
                item.append(0)
        data.append(item)

    for mechanic in Mechanic.objects.all().order_by('id'):
        for item in data:
            card_mechanics = CardMechanic.objects.filter(card_id=item[0].id, mechanic_id=mechanic.id)
            if card_mechanics:
                item.append(card_mechanics.first().effect_size)
            else:
                item.append(0)
    data = np.array(data)
    return data
