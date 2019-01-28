from collections import defaultdict

from node import AnonymousNode, BaseNode
from utils import expect
from literals import Literal

from .entity import Entity
from .interval import Interval


class RateLimit(AnonymousNode):
    def __init__(self, by, max, per, where=None):
        # XX: Hack, need actual rate limit implementation.
        self._state = defaultdict(int)

        where = where or Literal.List([])
        self.by = expect(Entity, by)
        self.max = expect(Literal.Number, max).unwrap()
        self.per = expect(Interval, per).unwrap()
        self.where = expect(Literal.List.Of(BaseNode), where)

    def get_dependent_nodes(self):
        return [self.by, self.where]

    def resolve(self, by, where):
        if where and not any(where):
            return False

        k = by.entity_path()

        self._state[k] += 1

        return self._state[k] > self.max
