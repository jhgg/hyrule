from node import AnonymousNode, BaseNode, ContainsNode
from utils import expect, Checker


class Literal(AnonymousNode):
    """
    A literal represents a node that resolves to a specific literal value, e.g. a number, string or list of nodes.
    """

    def get_dependent_nodes(self):
        return []

    def __repr__(self):
        return '<%s %r>' % (
            self.__class__.__name__,
            self.value
        )


class NumberLiteral(Literal):
    def __init__(self, value):
        self.value = expect((float, long, int), value)

    def resolve(self):
        return self.value

    unwrap = resolve


class BoolLiteral(Literal):
    def __init__(self, value):
        self.value = expect(bool, value)

    def resolve(self):
        return self.value

    unwrap = resolve


class NoneLiteral(Literal):
    value = None

    def __init__(self, value):
        expect(type(None), value)

    def resolve(self):
        return None

    unwrap = resolve


class StringLiteral(Literal):
    def __init__(self, value):
        self.value = expect((str, unicode), value)

    def resolve(self):
        return self.value

    unwrap = resolve


class ListLiteral(Literal):
    def __init__(self, value):
        self.value = expect(list, value)
        expect(Literal.List.Of(BaseNode), self)

    def get_dependent_nodes(self):
        return self.value

    def resolve(self, *args):
        return list(args)

    def contains(self, item):
        return ContainsNode(self, item)


class ListLiteralOf(Checker):
    def __init__(self, *types):
        self.types = types

    def check(self, literal):
        literal = expect(ListLiteral, literal)
        for item in literal.value:
            expect(self.types, item)

        return literal


Literal.List = ListLiteral
Literal.List.Of = ListLiteralOf
Literal.Number = NumberLiteral
Literal.String = StringLiteral
Literal.Bool = BoolLiteral
Literal.None_ = NoneLiteral
