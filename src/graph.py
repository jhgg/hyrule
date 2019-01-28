from collections import defaultdict, OrderedDict

from ast_utils import LITERAL_GLOBAL_KEY, transform_ast
from literals import Literal
from nodes import GLOBAL_ENTITIES
from nodes.data import Data
from nodes.rule import WhenRules
from node import AnonymousNode, NamedNode


class NodeNamespace(dict):
    """
    A namespace that the transformed AST will evaluate in, which does implciit
    binding of globals assigned to this namespace to NamedNodes, if the global is 
    an AnonymousNode. Also prevents re-defining globals.
    """

    def __setitem__(self, key, value):
        # Do not allow keys to be overwritten, they should be unique.
        if key in self:
            raise KeyError('Cannot overwrite key %r' % key)

        # If the value is an AnonymousNode, since we know the name it's being bound to,
        # promote it to a NamedNode.
        if isinstance(value, AnonymousNode):
            value = NamedNode(key, value)

        super(NodeNamespace, self).__setitem__(key, value)

    def iter_named_nodes(self):
        """
        Iterate over the named nodes that exist in this namespace.
        """
        for v in self.itervalues():
            if isinstance(v, NamedNode):
                yield v


BASE_GLOBALS = dict(GLOBAL_ENTITIES)
BASE_GLOBALS.update({
    LITERAL_GLOBAL_KEY: Literal,
})


def build(code):
    """
    Takes a code snippet containing our subset of python rules DSL, and building
    the dependency graph that will then be passed to an executor for evaluation.
    """
    # Phase 1, transform the AST, validating that the code is our subset of python
    # we are using to represent rules.
    transformed_ast = transform_ast(code)

    # Compile the transformed ast, ready for evaluation in the context of an exec.
    compiled = compile(transformed_ast, '<string>', 'exec')

    # This is the dependency graph that will be computed as we evaluate the rules code.
    dependency_graph = defaultdict(set)

    # This is a big hack lol.
    def when_rules_tracker(*args, **kwargs):
        node = WhenRules(*args, **kwargs)
        dependency_graph[node]
        return node

    # This is the globals where we'll traverse to resolve the dependency chained,
    # starting at named nodes within this dictionary.
    base_globals = dict(BASE_GLOBALS)
    base_globals['WhenRules'] = when_rules_tracker
    namespace = NodeNamespace(base_globals)

    # Run the code, which should evaluate all nodes.
    exec compiled in namespace

    def build_dependency_graph(node):
        """
        For each node, recurse down its dependencies, building the dependency graph.
        """
        dependency_graph[node]
        for dependent_node in node.get_dependent_nodes():
            dependency_graph[dependent_node].add(node)
            build_dependency_graph(dependent_node)

    # Start the traversal by crawling the named nodes, and traversing up their dependency
    # chain to discover the dependency graph.
    for node in namespace.iter_named_nodes():
        build_dependency_graph(node)

    return dependency_graph


def execute(dependency_graph, data):
    """
    Given a dependency graph and input data, evaluate the rules for a given event.

    Returning all the output named nodes within the dependency graph, to their resolved value,
    and also the side-effects (entity label mutations) that should take place as result of this
    execution.
    """

    # This is a mapping of node (by identity) to its resolved value.
    # Initially the only node that is resolved is the magic "Data" node, which is resolved to
    # the data that will seed this evaluation.
    resolved = {
        Data: data
    }

    def resolve(node):
        """
        Resolves the value of a node by recursively resolving its dependent nodes until the node is 
        able to be resolved.
        """
        deps = node.get_dependent_nodes()
        args = []
        for dep in deps:
            args.append(memoized_resolve(dep))

        if args and all(a is None for a in args):
            return None

        return node.resolve(*args)

    def memoized_resolve(node):
        """
        Resolves a node, storing the value of the resolve in `resolved`, essentially memoizing
        the resulting computation of said node.
        """
        if node not in resolved:
            resolved[node] = resolve(node)

        return resolved[node]

    # Execute the dependency graph.
    for parent_node, dependent_nodes in dependency_graph.items():
        for node in dependent_nodes:
            memoized_resolve(node)

        memoized_resolve(parent_node)

    result = {}
    actions = []

    # Extract values out of the resolved nodes.
    for node, resolved_value in resolved.items():
        # If encountering a WhenRules node, the evaluation result are actions,
        # which we want to collect.
        if isinstance(node, WhenRules) and resolved_value:
            actions.extend(resolved_value)
        # If encountering a NamedNode, we want to store the resolved value,
        # and return it to the caller.
        elif isinstance(node, NamedNode):
            result[node.name] = resolved_value

    return ExecutionResult(result, actions)


class ExecutionResult(object):
    def __init__(self, data, actions):
        self.data = data
        self.actions = actions
