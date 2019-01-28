from utils import expect, Checker


class ComparisonMixin(object):
    """
    The comparison mixin implements node comparsion types that make it so nodes can
    be compared to other nodes during execution
    """

    def __eq__(self, other):
        return CmpNode(self, other, lambda a, b: a == b)

    def __ne__(self, other):
        return InvertNode(CmpNode(self, other, lambda a, b: a == b))

    def in_(self, collection):
        return ContainsNode(collection, self)

    def __or__(self, other):
        return CmpNode(self, other, lambda a, b: bool(a or b))

    def __and__(self, other):
        return CmpNode(self, other, lambda a, b: bool(a and b))

    def __gt__(self, other):
        return CmpNode(self, other, lambda a, b: a > b)

    def __ge__(self, other):
        return CmpNode(self, other, lambda a, b: a >= b)

    def __lt__(self, other):
        return CmpNode(self, other, lambda a, b: a < b)

    def __le__(self, other):
        return CmpNode(self, other, lambda a, b: a <= b)

    def __invert__(self):
        return InvertNode(self)


class BaseNode(object):
    """
    This is the base node type that all nodes must implement.

    Generally, you do not subclass this directly, and instead subclass AnonymousNode
    """

    def get_dependent_nodes(self):
        """
        Return a list of nodes that must resolve before this node can resolve.
        """
        raise NotImplementedError(self)

    def resolve(self, *args):
        """
        Resolves this node. The value of args is the resolved node dependencies 
        that we returned in `get_dependent_nodes`, in the order they were specified.
        """
        raise NotImplementedError(self)


class AnonymousNode(BaseNode, ComparisonMixin):
    """
    A node that does not have a name bound to it.
    """
    # XX: Implement this check.
    anonymous_only = False


class ContainsNode(AnonymousNode):
    def __init__(self, collection, item):
        from literals import Literal

        self.collection = expect(Literal.List, collection)
        self.item = expect(BaseNode, item)

    def get_dependent_nodes(self):
        return [self.collection, self.item]

    def resolve(self, collection, item):
        return any(
            c == item
            for c in collection
        )


class CmpNode(AnonymousNode):
    """
    A node that executes the `comparitor` against the resolved values of the provided nodes (a, b).
    """

    def __init__(self, a, b, comparitor):
        self.a = expect(BaseNode, a)
        self.b = expect(BaseNode, b)
        self.resolve = comparitor

    def get_dependent_nodes(self):
        return [self.a, self.b]


class InvertNode(AnonymousNode):
    """
    A node that does a bool not against the resolved value of the provided nodes.
    """

    def __init__(self, a):
        self.a = expect(BaseNode, a)

    def get_dependent_nodes(self):
        return [self.a]

    def resolve(self, a):
        return bool(not a)


class NamedNode(BaseNode, ComparisonMixin):
    """
    Wraps an anonymous node, binding it to a name that will be used in the result of the execution of the
    rules graph. This node essentailly will export the resolved value back to the caller, in a dictionary 
    keyed by `name`.
    """

    def __init__(self, name, node):
        self.name = name
        self.node = expect(AnonymousNode, node)

    def __repr__(self):
        return '<NamedNode name=%r, node=%r>' % (self.name, self.node)

    def get_dependent_nodes(self):
        return self.node.get_dependent_nodes()

    def resolve(self, *args):
        return self.node.resolve(*args)

    def __getattr__(self, attribute):
        return getattr(self.node, attribute)


class NamedNodeOf(Checker):
    """
    A checker that will assert that the node is a named node, and the wrapped node is of a certain node type.
    """

    def __init__(self, contained_type):
        self.contained_type = contained_type

    def check(self, item):
        expect(NamedNode, item)
        expect(self.contained_type, item.node)

        return item


NamedNode.Of = NamedNodeOf
