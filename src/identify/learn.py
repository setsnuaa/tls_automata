# -*- coding：utf-8 -*-
# 将状态机聚合成状态树

import ast
import json
from pathlib import Path

import networkx
import pydot
from networkx.algorithms.traversal.depth_first_search import dfs_tree


class ModelTree(networkx.DiGraph):
    # 父节点
    def parent(self, node):
        return list(self.predecessors(node))[0]

    # 所有叶节点
    @property
    def leaves(self):
        return [node for node in self.nodes if self.out_degree(node) == 0]

    # 所有状态机
    @property
    def models(self):
        return {
            _models for leaf in self.leaves for _models in self.nodes[leaf]["models"]
        }

    # 以传入节点为根的子树
    def subtree(self, node):
        subtree_nodes = dfs_tree(self, node).nodes
        return self.subgraph(subtree_nodes)

    # 删除节点
    def prune_node(self, node):
        try:
            parent = self.parent(node)
            if self.out_degree(parent) == 1:
                self.prune_node(parent)
        except IndexError:
            pass

        self.remove_node(node)

    # 删除状态机
    def prune_models(self, models):
        models = set(models)
        for leaf in self.leaves:
            self.nodes[leaf]["models"] -= models
            if not self.nodes[leaf]["models"]:
                self.prune_node(leaf)

    # 缩短分支长度
    def condense(self):
        # 删除包含所有状态机的叶节点
        models = self.models
        for leaf in self.leaves:
            if self.nodes[leaf]["models"] == models:
                self.prune_node(leaf)
        # 缩短路径长度
        ancestors = {self.parent(self.parent(leaf)) for leaf in self.leaves}
        tree_start_size = len(self)
        for node in ancestors:
            subtree = self.subtree(node)
            leaves = subtree.leaves
            models = subtree.models

            # For every available input, we check if it is redundant. This is
            # the case when:
            # - The input only has one possible output.
            # - This output leads to a leaf node.
            redundant_nodes = set()
            for input_node in subtree[node]:
                output_nodes = list(subtree.neighbors(input_node))
                if len(output_nodes) == 1 and output_nodes[0] in leaves:
                    # If this is the case, these nodes as redundant
                    redundant_nodes.update([input_node, output_nodes[0]])

            # Remove the redundant nodes
            self.remove_nodes_from(redundant_nodes)

            # After (possibly) removing some paths, we now check if the
            # ancestor has any paths lefts in the original tree.
            if self.out_degree(node) == 0:
                # If not, we move the information about the models to this
                # node.
                self.nodes[node]["models"] = models

        # If the tree has changed, condense it again
        if len(self) != tree_start_size:
            self.condense()

    # 画出状态树
    def draw(self, fmt="dot", path=None):
        try:
            model_count = len(self.models)
        except KeyError:
            pass

        # Relabel all the nodes
        for node in self.nodes:
            if self.out_degree(node) == 0:
                # Leaf node
                try:
                    models = sorted(self.nodes[node]["models"])
                    model_share = "{:.2f}%".format(100 * len(models) / model_count)
                    self.nodes[node]["label"] = "\n".join([model_share] + models)
                except KeyError:
                    self.nodes[node]["label"] = ""
                self.nodes[node]["shape"] = "rectangle"
            else:
                # Not a leaf node
                self.nodes[node]["label"] = ""
        dot = networkx.drawing.nx_pydot.to_pydot(self)
        result = dot.create(format=fmt)

        if path:
            with open(path, "wb") as file:
                file.write(result)

        return dot.create(format=fmt)


# 规范化
def normalize_graph(dot_graph: str, *, max_depth=10) -> ModelTree:
    """
    Args:
        dot_graph: The DOT representation of the input graph
        max_depth: The maximum depth of the tree, especially relevant when the
            graph contains cycles.
    Returns:
        A normalized ModelTree which represents the input graph.
    """
    graph = _dot_to_networkx(dot_graph)

    # Assumes there is a node called '__start0', which is connected a single
    # node in the graph (the entry point)
    graph_root = list(graph["__start0"])[0]

    # Create the ModelTree that will contain the normalized graph
    tree = ModelTree()
    tree_root = ()
    tree.add_node(tree_root)

    # Normalize the graph by recursively merging into the tree
    return _merge_subgraph(tree, tree_root, graph, graph_root, 0, max_depth)


# 将状态机转换为树
# dfs
def _merge_subgraph(
        tree: ModelTree,
        root: tuple,
        graph: networkx.DiGraph,
        current_node: str,
        current_depth: int,
        max_depth: int,
) -> ModelTree:
    """Recursively merge a directed graph into the passed ModelTree. This is an
    internal function that is called from `normalize_graph`.
    Args:
        tree: The tree that is being constructed, and into which the graph will
            be merged.
        root: The current root node of the tree, the graph will be merged
            beginning at this node.
        graph: The graph to merge into the tree
        current_node: The current node of the graph to merge
        current_depth: The current recursion depth, this function aborts when
            depth > max_depth.
        max_depth: The maximum recursion depth, primaraly useful to escape
            cycles, so it should be higher than the valid depth of the tree.
    """
    # If we exceeded the max depth, we stop
    if current_depth > max_depth:
        return tree

    neighbors = list(graph[current_node])

    # If a node has no neighbors, there is nothing to do and this function
    # returns immediately.
    if not neighbors:
        return tree

    # A node can have multiple neighbors
    for neighbor in neighbors:

        # There can be multiple edges between two nodes, each with
        # a different label. Each edge is numbered, but we ignore this
        # number.
        for _, edge in graph[current_node][neighbor].items():
            received_node = _merge_path_from_label(tree, root, edge["label"])

            # 当状态机的一条边的输出为EOF的时候，说明遍历到了终止状态，停止遍历
            if "EOF" in received_node[-1]:
                # Do not recurse
                continue

            # 吸收态也停止遍历
            if neighbors == [current_node]:
                continue

            # Recurse with new root and current node
            tree = _merge_subgraph(
                tree, received_node, graph, neighbor, current_depth + 1, max_depth
            )

    return tree


def _merge_path_from_label(tree: ModelTree, root: tuple, label: str) -> tuple:
    """Merge a path into the passed tree from a label. The label is assumed to
    have the format "{{ sent }} / {{ received }}", since this is the format
    that StateLearner outputs. The nodes will be added as
        root -> sent -> received
    with the appropriate edge labels.
    Args:
        tree: The path will be added to this graph.
        root: Point in the tree where the nodes will be added.
        label: String of the format "{{ sent }} / {{ received }}"
    Returns:
        The name of the "received" node (which is a tuple), so the caller knows
        the endpoint of the added path.
    """
    # We start by extracting the sent and received messages. Split the label
    # in the sent and received message. Remove the double quotes and the excess
    # whitespace.
    sent, received = [
        message.replace('"', "").strip() for message in label.split("/", maxsplit=1)
    ]

    # Append the sent and received messages to the tree
    # 节点编码
    sent_node = root + (sent,)
    received_node = root + (sent, received)
    tree.add_edge(root, sent_node, label=sent)
    tree.add_edge(sent_node, received_node, label=received)

    return received_node


def _dot_to_networkx(dot_graph):
    """Convert a DOT string to a networkx graph."""
    # Read the input graph using `graph_from_dot_data()`. This function returns
    # a list but StateLearner only puts a single graph in a file. We assume
    # this graph is present and do not check the length. A KeyError will
    # notify us in case of an error.
    pydot_graph = pydot.graph_from_dot_data(dot_graph)[0]

    # Convert to networkx graph
    return networkx.drawing.nx_pydot.from_pydot(pydot_graph)


def construct_tree_from_dedup(directory: str, tree_type: str) -> ModelTree:
    """Given a directory output from the dedup command, construct a ModelTree.
    Args:
        directory: The path to the dedup directory
        tree_type: The desired output tree type, can be any from
            SUPPORTED_TREE_TYPES.
    """
    try:
        handler = _tree_type_handlers[tree_type]
    except KeyError:
        raise ValueError(f"Not a valid tree type: {tree_type}")

    path = Path(directory)

    # Build the tree using the specified tree type handler
    tree = handler(path)

    # Add the model mapping information to the tree
    tree.model_mapping = {}

    model_directories = sorted([item for item in path.iterdir() if item.is_dir()])
    for model_dir in model_directories:
        with open(model_dir / "versions.json") as f:
            version_info = json.load(f)

            # Convert to set with tuples and add to model_mapping
            version_info = {tuple(x) for x in version_info}
            tree.model_mapping[model_dir.name] = version_info

    return tree


def _construct_hdt(path: Path) -> ModelTree:
    tree = ModelTree()
    tree_root = ()
    tree.add_node(tree_root)

    model_directories = sorted([item for item in path.iterdir() if item.is_dir()])
    for model_dir in model_directories:
        with open(model_dir / "model.gv") as f:
            # 将状态机转换为树
            graph = normalize_graph(f.read())
            # 合并树
            tree.add_edges_from(graph.edges(data=True))
            for leaf in graph.leaves:
                try:
                    # 如果状态机树的叶节点与状态树叶节点重合，那么说明该叶节点对应的
                    # 状态机共享从根节点到叶节点的路径，将新加入的状态机名称加入该叶节点
                    tree.nodes[leaf]["models"].add(model_dir.name)
                except KeyError:
                    # 状态树中没有状态机树的叶节点，说明是新的叶节点，创建一个字典
                    tree.nodes[leaf]["models"] = {model_dir.name}

    tree.condense()
    return tree


_tree_type_handlers = {"hdt": _construct_hdt}
SUPPORTED_TREE_TYPES = list(_tree_type_handlers.keys())
