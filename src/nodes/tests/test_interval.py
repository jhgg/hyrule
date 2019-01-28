import pytest
from datetime import timedelta

from nodes.interval import Interval
from literals import Literal

N = Literal.Number


@pytest.mark.parametrize('interval, resolved', [
    (Interval(N(5)), timedelta(seconds=5)),
    (Interval.Seconds(N(5)), timedelta(seconds=5)),
    (Interval.Minutes(N(1)), timedelta(seconds=60)),
    (Interval.Hours(N(1)), timedelta(seconds=60 * 60)),
    (Interval.Days(N(1)), timedelta(seconds=60 * 60 * 24)),
    (Interval.Days(N(1.5)), timedelta(seconds=60 * 60 * 24 * 1.5)),
    (Interval.Weeks(N(1)), timedelta(seconds=60 * 60 * 24 * 7)),
])
def test_interval(interval, resolved):
    assert interval.unwrap() == resolved
