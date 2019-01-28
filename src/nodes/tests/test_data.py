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


def test_data_extraction():
    data = run('''
        NotExists = JsonData('$.wtf')
        NotExists2 = JsonData('$.bar.baz')
        Bar = JsonData('$.bar')
        Baz = JsonData('$.baz.qux')

        T1 = Bar == "bar_value"
        T2 = Bar != "not_bar_value"
        T3 = ["foo", "qux_value"].contains(Baz)
    ''', {
        'bar': 'bar_value',
        'baz': {'qux': 'qux_value'}
    })

    assert data == {
        'NotExists': None,
        'NotExists2': None,
        'Bar': 'bar_value',
        'Baz': 'qux_value',
        'T1': True,
        'T2': True,
        'T3': True,
    }
