class Environment:

    self.domain = []
    self.card_creator_agents = []
    self.gatekeepers = []
    self.deck_creators = []

    def __init__(self):
        ...

    def step(self):
        return [agent.act() for agent in deck_creators]
