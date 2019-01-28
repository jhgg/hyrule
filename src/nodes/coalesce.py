from node import BaseNode, AnonymousNode
from utils import expect


class Coalesce(AnonymousNode):
    """
    Returns the first node of the provided nodes that is not None, 
    or None if all nodes resolve to None.
    """

    def __init__(self, *nodes):
        self.nodes = [expect(BaseNode, node) for node in nodes]

    def get_dependent_nodes(self):
        return self.nodes

    def resolve(self, *nodes):
        for node in nodes:
            if node is not None:
                return node
