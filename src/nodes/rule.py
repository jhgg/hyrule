from node import AnonymousNode, NamedNode
from utils import expect
from literals import Literal

from .entity import Entity


class LabelAction(object):
    def __init__(self, entity, label, status):
        self.entity = entity
        self.label = label
        self.status = status
        self.rules_with_reasons = {}

    def __repr__(self):
        return '<LabelAction entity=%r, label=%r, status=%r, rules=%r>' % (
            self.entity,
            self.label,
            self.status,
            self.rules_with_reasons
        )


class Rule(AnonymousNode):
    def __init__(self, when, reason=None):
        self.when = expect(Literal.List, when)
        self.reason = expect(Literal.String, reason).unwrap()

    def get_dependent_nodes(self):
        return [self.when]

    def resolve(self, when):
        return any(when)


class WhenRules(object):
    def __init__(self, rules, then):
        self.rules = expect(
            Literal.List.Of(NamedNode.Of(Rule)), rules,
        )
        self.then = expect(Literal.List.Of(RuleLabelOperation), then)

    def get_dependent_nodes(self):
        return [self.rules, self.then]

    def resolve(self, rules, then):
        rules_and_reasons = {}

        def add_reasons(node):
            if not (isinstance(node, NamedNode) and isinstance(node.node, Rule)):
                return

            rule = node.node
            rules_and_reasons[node.name] = node.reason

            # Recursively add reasons for nested rules.
            for node in rule.when.value:
                add_reasons(node)

        for node, result in zip(self.rules.value, rules):
            if not result:
                continue

            add_reasons(node)

        if rules_and_reasons:
            for action in then:
                action.rules_with_reasons = rules_and_reasons

            return then

        return []


class RuleLabelOperation(AnonymousNode):
    def __init__(self, entity, label):
        self.entity = expect(Entity, entity)
        self.label = expect(Literal.String, label).unwrap()

    def get_dependent_nodes(self):
        return [self.entity]


class RuleAddLabel(RuleLabelOperation):
    def resolve(self, entity):
        return LabelAction(
            entity=entity,
            label=self.label,
            status='ADDED'
        )


class RuleRemoveLabel(RuleLabelOperation):
    def resolve(self, entity):
        return LabelAction(
            entity=entity,
            label=self.label,
            status='REMOVED'
        )


class Label(object):
    pass


Label.Add = RuleAddLabel
Label.Remove = RuleRemoveLabel
