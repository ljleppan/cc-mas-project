import aiomas

from creamas.core import CreativeAgent, Artifact

def CardAgetn(CreativeAgent):

    def __init__(self, env, generator, evaluator):
        super().__init__(env)
        self._generator = generator
        self._evaluator = evaluator

    def evaluate(self, artifact):
        return self._evaluate(artifact)
