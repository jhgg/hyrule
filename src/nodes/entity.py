from node import AnonymousNode
from utils import expect
from literals import Literal


class Entity(AnonymousNode):
    """
    A node that resolves to an EntityRef with the resolved value of the id.

    Example usage may look like:

        UserId = JsonData('$.user.id')
        User = Entity('User', UserId)

    User would be an EntityRef('User', 5), if the data provided was {"user": {"id": 5}}

    """

    def __init__(self, entity_type, entity_id):
        self.type = expect(Literal.String, entity_type).unwrap()
        self.id = expect(AnonymousNode, entity_id)

    def get_dependent_nodes(self):
        return [self.id]

    def resolve(self, entity_id):
        return EntityRef(self.type, entity_id)


class EntityRef(object):
    def __init__(self, entity_type, entity_id):
        self.type = entity_type
        self.id = entity_id

    def entity_path(self):
        return u'%s/%s' % (self.type, self.id)

    __unicode__ = entity_path

    def __repr__(self):
        return '<EntityRef %r>' % self.entity_path()

    def __eq__(self, other):
        # If we are comparing against an entity ref directly.
        if isinstance(other, EntityRef):
            return (
                self.id == other.id and
                self.type == other.type
            )

        # Otherwise, equality is implicit upon comparing against the ID.
        return self.id == other
