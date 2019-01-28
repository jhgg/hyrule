import ast

LITERAL_GLOBAL_KEY = '__internal_Literal'


class LiteralTransformer(ast.NodeTransformer):
    """
    This literal transformer finds constant literals, e.g. numbers, strings, lists, bools and None within the AST,
    converting them to their relevant Literal nodes (e.g. Literal.Number, etc...)

    This is useful so that any place we use a literal within the rules, they can be treated as nodes, which eases a lot of things,

    An example of this transformation is as follows:

        X = 1 < 2

    This transforms into:

        X = Literal.Number(1) < Literal.Number(2)

    Which then during the initial evaluation pass transforms to:

        X = CmpNode(Literal.Number(1), Literal.Number(2), lambda a, b: a < b)

    At all points, X remains a node, which can then be used in other places that expect a node.
    It also means that the actual comparison is deferred until the node is resolved in the graph.

    Additionally, X becomes a named node, meaning that the evaluation result of `CmpNode` will be bound to
    the name `X`, and it cannot be overwritten.
    """

    def literal_transform(self, attr, node):
        """
        Wraps a node with call to construct the literal.

        E.g. it will transform 2 into Literal.Number(2) within the code.
        """
        return ast.copy_location(ast.Call(
            func=ast.Attribute(
                value=ast.Name(id=LITERAL_GLOBAL_KEY, ctx=ast.Load()),
                attr=attr,
                ctx=ast.Load()
            ),
            args=[node],
            keywords=[],
        ), node)

    def visit_List(self, node):
        return self.literal_transform('List', self.generic_visit(node))

    def visit_Num(self, number):
        return self.literal_transform('Number', number)

    def visit_Str(self, string):
        return self.literal_transform('String', string)

    def visit_Name(self, name):
        if name.id == 'None':
            return self.literal_transform('None_', name)

        if name.id in ('True', 'False'):
            return self.literal_transform('Bool', name)

        return name

    # TODO: SyntaxError on AST that is superflous to the graph.


def transform_ast(code):
    ast_nodes = ast.parse(code)
    transformer = LiteralTransformer()
    transformed_nodes = transformer.visit(ast_nodes)

    # print ast.dump(transformed_nodes)
    return ast.fix_missing_locations(transformed_nodes)
