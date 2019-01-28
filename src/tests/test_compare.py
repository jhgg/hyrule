import harness
from nodes.entity import EntityRef


def test_equality():
    data = harness.run('''
        Foo = "hello"
        Bar = "world"
        FooEqA = Foo == "hello"
        FooEqB = "hello" == Foo
        FooEqC = "world" == Foo
        FooEqD = Foo == "world"
        FooEqBar = Foo == Bar
        BarEqFoo = Bar == Foo
        FooEqFoo = Foo == Foo
    ''')

    assert data == {
        'Foo': 'hello',
        'Bar': 'world',
        'FooEqA': True,
        'FooEqB': True,
        'FooEqC': False,
        'FooEqD': False,
        'FooEqBar': False,
        'BarEqFoo': False,
        'FooEqFoo': True
    }


def test_entity_equality():
    data = harness.run('''
        A = Entity('User', '1234')
        B = Entity('User', '1234')
        C = Entity('User', '4567')

        EqA = A == B
        EqB = B == A
        EqC = A == '1234'
        EqD = '1234' == A
        EqE = A == C
        EqF = C == A

        NeA = A != B
        NeB = A != '1234'
        NeC = A != '4567'
        NeD = A != C
    ''')

    assert data == {
        'A': EntityRef('User', '1234'),
        'B': EntityRef('User', '1234'),
        'C': EntityRef('User', '4567'),

        'EqA': True,
        'EqB': True,
        'EqC': True,
        'EqD': True,
        'EqE': False,
        'EqF': False,

        'NeA': False,
        'NeB': False,
        'NeC': True,
        'NeD': True,
    }


def test_in():
    data = harness.run('''
        A = [1, 2, 3]

        T = (2).in_(A)
        F = (4).in_(A)
    ''')

    assert data == {
        'A': [1, 2, 3],
        'T': True,
        'F': False,
    }


def test_list_lit_contains():
    data = harness.run('''
        A = [1, 2, 3]

        T = A.contains(2)
        F = A.contains(4)
    ''')

    assert data == {
        'A': [1, 2, 3],
        'T': True,
        'F': False,
    }


def test_cmp():
    data = harness.run('''
        A = 1
        B = 2

        TA = A < B
        TB = A <= A
        TC = B > A
        TD = B >= A

        FA = B < A
        FB = B <= A
        FC = A > B
        FD = A >= B
    ''')

    assert data == {
        'A': 1,
        'B': 2,

        'TA': True,
        'TB': True,
        'TC': True,
        'TD': True,

        'FA': False,
        'FB': False,
        'FC': False,
        'FD': False,
    }


def test_inv():
    data = harness.run('''
        F = ~True
        T = ~False
        # None negated is still None.
        N = ~None
    ''')

    assert data == {
        'F': False,
        'T': True,
        'N': None,
    }


def test_or():
    data = harness.run('''
        T1 = True | False
        T2 = True | True
        T3 = False | True
        T4 = False | False | True
        T5 = True | False | False
        T6 = False | True | False

        F = False | False
    ''')

    assert data == {
        'T1': True,
        'T2': True,
        'T3': True,
        'T4': True,
        'T5': True,
        'T6': True,
        'F': False,
    }


def test_and():
    data = harness.run('''
        T1 = True & True
        T2 = True & ~False
        T3 = ~False & ~False
        T4 = ~False & True
        T5 = True & True & True

        F1 = False & False
        F2 = False & False & False
    ''')

    assert data == {
        'T1': True,
        'T2': True,
        'T3': True,
        'T4': True,
        'T5': True,
        'F1': False,
        'F2': False,
    }


def test_combined():
    data = harness.run('''
        T1 = True & True
        T2 = T1 & True
        T3 = T2 & True
        T4 = T1 & T2 & T3

        F1 = ~T1
        F2 = ~T2
        F3 = ~T3
        F4 = ~T4
    ''')

    assert data == {
        'T1': True,
        'T2': True,
        'T3': True,
        'T4': True,
        'F1': False,
        'F2': False,
        'F3': False,
        'F4': False,
    }
