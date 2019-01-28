import harness


def test_json_data_extraction():
    data = harness.run('''
        Foo = JsonData('$.foo')
    ''', {'foo': 'bar'})

    assert data == {
        'Foo': 'bar'
    }


def test_num_literal():
    data = harness.run('''
        One = 1
    ''')

    assert data == {
        'One': 1
    }


def test_string_literal():
    data = harness.run('''
        Str = "hello world"
    ''')

    assert data == {
        'Str': 'hello world'
    }


def test_list_literal():
    data = harness.run('''
        List = [1, 2.5, "hello", [3, 4], True, False, None]
    ''')

    assert data == {
        'List': [1, 2.5, "hello", [3, 4], True, False, None]
    }


def test_bool_literal():
    data = harness.run('''
        T = True
        F = False
    ''')

    assert data == {
        'T': True,
        'F': False
    }


def test_none_literal():
    data = harness.run('''
        N = None
    ''')

    assert data == {
        'N': None
    }
