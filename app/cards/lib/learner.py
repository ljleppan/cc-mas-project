import numpy as np

from cards.models import *
from sklearn.linear_model import RidgeCV

def learn():
    print("Learning to evaluate card values")

    try:
        data = np.load("heathstonedata.npy")
        print("Loaded card data from cache")
    except Exception:
        print("Did not find cached data, reading from DB (This WILL take ~10 minutes)")
        data =  _data_as_numpy_array()
        print("Loading complete, caching data")
        np.save("heathstonedata.npy", data)
        print("Caching complete")

    cards = data[:, 0]

    y = np.ascontiguousarray(data[:, 1], dtype=np.float)
    X = np.ascontiguousarray(data[:, 2:], dtype=np.float)

    print("Learning coefficients using 5 times cross validated Lasso")
    model = RidgeCV()
    model.fit(X, y)

    print("Learning complete.")
    print("\tAccuracy: {}".format(model.score(X, y)))
    
    coeffs = model.coef_
    print(coeffs.shape)
    _save_coefficients(coeffs)

def _save_coefficients(coeffs):

    MetaData.objects.filter(name="health_coeff").update(value=coeffs[0])
    MetaData.objects.filter(name="minion_attack_coeff").update(value=coeffs[1])
    MetaData.objects.filter(name="durability_coeff").update(value=coeffs[2])
    MetaData.objects.filter(name="weapon_attack_coeff").update(value=coeffs[3])

    # Since we are only doing updates, the post_save hooks do not get
    # called. So we need to ensure that all cards get their simple_value
    # fields refreshed. We do this by simply calling save() on a random
    # metadata field, which causes a refresh for all cards.
    MetaData.objects.first().save()

    coeffs = coeffs[4:]

    i = 0
    for ctype in CardType.objects.all().order_by('id'):
        ctype.value = coeffs[i]
        ctype.save()
        i+=1

    for race in Race.objects.all().order_by('id'):
        race.value = coeffs[i]
        race.save()
        i+=1

    for mechanic in Mechanic.objects.all().order_by('id'):
        mechanic.value = coeffs[i]
        mechanic.save()
        i += 1

def _data_as_numpy_array():
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
