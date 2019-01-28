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
    return result.data, result.actions


def test_rule_simple():
    data, actions = run('''
        T = Rule(when=[True], reason='True')
        TT = Rule(when=[True, False], reason='Or')
        F = Rule(when=[False], reason='False')
        FF = Rule(when=[False, False], reason='False')
    ''')

    assert data == {
        'T': True,
        'TT': True,
        'F': False,
        'FF': False,
    }
    assert actions == []


def test_rule_nested():
    from nodes.entity import EntityRef

    data, actions = run('''
        T = Rule(when=[True], reason='Base True')
        TT = Rule(when=[T], reason='Nested True 1')
        TTT = Rule(when=[TT], reason='Nested True 2')

        F = Rule(when=[False], reason='Base False')
        FF = Rule(when=[F], reason='Nested False')

        WhenRules(
            rules=[TTT, F, FF],
            then=[
                Label.Add(Entity('User', 1), 'bad_user')
            ]
        )
    ''')
    assert data == {
        'T': True,
        'TT': True,
        'TTT': True,
        'F': False,
        'FF': False,
    }

    assert len(actions) == 1
    action = actions[0]
    assert action.entity == EntityRef('User', 1)
    assert action.label == 'bad_user'
    assert action.status == 'ADDED'
    assert action.rules_with_reasons == {
        'T': 'Base True',
        'TT': 'Nested True 1',
        'TTT': 'Nested True 2',
    }


def test_when_rules():
    from nodes.entity import EntityRef

    data, actions = run('''
        U = Entity('User', 1)
        T = Rule(when=[True], reason='I am true!')
        F = Rule(when=[False], reason='I am false!')

        WhenRules(
            rules=[T, F],
            then=[
                Label.Add(U, 'bad_user')
            ]
        )
    ''')

    assert data == {
        'U': 1,
        'T': True,
        'F': False
    }

    assert len(actions) == 1
    action = actions[0]

    assert action.entity == EntityRef('User', 1)
    assert action.label == 'bad_user'
    assert action.status == 'ADDED'
    assert action.rules_with_reasons == {
        'T': 'I am true!'
    }

# XX: Validate non rules dont work in WhenRules
