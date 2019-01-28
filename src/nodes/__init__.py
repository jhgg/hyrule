from .data import JsonData
from .entity import Entity
from .rule import Rule, WhenRules, Label
from .has_label import HasLabel
from .rate_limit import RateLimit
from .coalesce import Coalesce
from .interval import Interval

GLOBAL_ENTITIES = {
    'Coalesce': Coalesce,
    'Entity': Entity,
    'JsonData': JsonData,
    'HasLabel': HasLabel,
    'Rule': Rule,
    'WhenRules': WhenRules,
    'Label': Label,
    'RateLimit': RateLimit,
    'Interval': Interval,
}
