import jsonpath_rw

from node import AnonymousNode
from utils import expect
from literals import Literal


class Data(AnonymousNode):
    """
    A magic placeholder that will resolve to the data provided to the executor.
    """

    def get_dependent_nodes(self):
        return []

    def resolve(self):
        raise RuntimeError(
            'Data.resolve was called, and it should never be called. This is probably a bug.'
        )


Data = Data()


class JsonData(AnonymousNode):
    """
    A node that will extract a value from the execution data, by evaluating a json path.

    Example usage: JsonData('$.user.id')
    Given the data: {"user": {"id": 5}}, would resolve to `5`.
    """

    def __init__(self, selector):
        self.selector = jsonpath_rw.parse(
            expect(Literal.String, selector).unwrap()
        )

    def resolve(self, data):
        result = self.selector.find(data)
        if not result:
            return None

        return result[0].value

    def get_dependent_nodes(self):
        return [Data]
