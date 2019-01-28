from datetime import timedelta

from node import BaseNode, AnonymousNode
from utils import expect
from literals import Literal


class Interval(AnonymousNode):
    """
    Represents an interval of time. Resolves to a timedelta.
    """

    anonymous_only = True

    def __init__(self, seconds):
        self.seconds = expect(Literal.Number, seconds).unwrap()

    def resolve(self):
        return timedelta(seconds=self.seconds)

    unwrap = resolve


def interval_with_magnitude(magnitude):
    @staticmethod
    def wrapped(seconds):
        value = expect(Literal.Number, seconds).unwrap()
        value *= magnitude
        return Interval(Literal.Number(value))

    return wrapped


Interval.Seconds = interval_with_magnitude(1)
Interval.Minutes = interval_with_magnitude(60)
Interval.Hours = interval_with_magnitude(60 * 60)
Interval.Days = interval_with_magnitude(60 * 60 * 24)
Interval.Weeks = interval_with_magnitude(60 * 60 * 24 * 7)
