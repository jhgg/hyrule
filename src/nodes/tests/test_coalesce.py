import graph


def dedent(c):
    return '\n'.join(c.strip() for c in c.splitlines())


execute = graph.execute


def build(code):
    return graph.build(dedent(code))

# XX: clean to file


def run(code, data=None):
    graph = build(code)
    data = data or {}
    result = execute(graph, data)
    return result.data


def test_coalesce():
    data = run('''
        A = Coalesce(1, None)
        B = Coalesce(None, 2)
        C = Coalesce(None, None)
    ''')

    assert data == {
        'A': 1,
        'B': 2,
        'C': None
    }
