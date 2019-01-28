from collections import defaultdict
from node import AnonymousNode
from nodes.entity import Entity
from literals import Literal
from utils import expect

# XX: Hack, need actual entity label implementation.
entity_labels = defaultdict(dict)


class HasLabel(AnonymousNode):
    """
    A node which will take an entity + label + status, and resolve a boolean as to
    whether or not the entity the given label in the status provided.
    """

    def __init__(self, entity, label, status):
        self.entity = expect(Entity, entity)
        self.label = expect(Literal.String, label).unwrap()
        self.status = expect(Literal.String, status).unwrap()

        assert self.status in {'ADDED', 'REMOVED'}

    def get_dependent_nodes(self):
        return [self.entity]

    def resolve(self, entity):
        k = entity.entity_path()
        return entity_labels.get(k, {}).get(self.label) == self.status


def has_label_added(entity, label):
    return HasLabel(entity, label, Literal.String('ADDED'))


def has_label_removed(entity, label):
    return HasLabel(entity, label, Literal.String('REMOVED'))


HasLabel.Added = has_label_added
HasLabel.Removed = has_label_removed
