import graph


def dedent(c):
    return '\n'.join(c.strip() for c in c.splitlines())


execute = graph.execute


def build(code):
    return graph.build(dedent(code))


def run(code, data=None):
    graph = build(code)
    print graph
    data = data or {}
    result = execute(graph, data)
    return result.data
