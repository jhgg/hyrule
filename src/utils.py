class Checker(object):
    """
    Subclass this to implement more specific type-checks to customize the behavior
    of `expect`. A good example is in `Literal.List.Of`.
    """

    def check(self, item):
        """
        Implement this to perform checks, raising an exception if the check fails. You must return `item` from
        this function.
        """
        raise NotImplementedError()


def expect(what, item):
    """
    A utility function which performs runtime type-checks. 

    In the general case, `expect` should be used in the construction of a node, to ensure that the nodes that are 
    provided are of a certain type.

    e.g.:

        class SumNode(AnonymousNode):
            def __init__(self, a, b):
                self.a = expect(Literal.Number, a)
                self.b = expect(Literal.Number, b)

            ...

    Or to just assert something /is/ a node...

        class SumNode(AnonymousNode):
            def __init__(self, a, b):
                self.a = expect(BaseNode, a)
                self.b = expect(BaseNode, b)

    """
    from node import NamedNode

    try:
        if len(what) == 1:
            what = what[0]
    except TypeError:
        pass

    if isinstance(what, Checker):
        checked = what.check(item)
        if checked is not item:
            raise RuntimeError(
                'Checker %r returned %r, expected %r' % (what, checked, item)
            )
        return checked

    if isinstance(item, what):
        return item

    if isinstance(item, NamedNode) and isinstance(item.node, what):
        return item

    raise TypeError('Expected type %r, got %r' % (what, item))
