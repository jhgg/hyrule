import graph


def dedent(c):
    return '\n'.join(c.strip() for c in c.splitlines())


execute = graph.execute


def build(code):
    return graph.build(dedent(code))


def test_rate_limit_basic():
    graph = build('''
        User = Entity('User', 1)

        RateLimitSimple = RateLimit(
            by=User,
            max=2,
            per=Interval.Minutes(1)
        )
    ''')

    for _ in xrange(2):
        a = execute(graph, {}).data
        assert a['RateLimitSimple'] == False

    b = execute(graph, {}).data
    assert b['RateLimitSimple'] == True
