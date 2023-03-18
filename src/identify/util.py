# -*- coding：utf-8 -*-
from collections import defaultdict
from pathlib import Path

import networkx
from automata.automata import load_automaton_from_file


# 从dot文件读取状态机并去重
# 目录结构：state_machine/implementation/version/tls_version/model.dot
# eg.state_machine/openssl/3.0.0/tls12/model.dot
# 保存指纹的数据结构为dict(tls_version,dict(fingerprint,list(client_version))
def dedup_state_machine_dir(state_machine_directory):
    root = Path(state_machine_directory)
    results = defaultdict(lambda: defaultdict(list))

    for implementation_path in root.iterdir():
        implementation_results = dedup_implementation_dir(implementation_path)
        for protocol, state_machine_dicts in implementation_results.items():
            for state_machine, client_version in state_machine_dicts.items():
                # model为字典的key，相同model会将对应客户端版本合并到list中
                results[protocol][state_machine] += client_version

    return results


def dedup_implementation_dir(implementation_path):
    results = defaultdict(lambda: defaultdict(list))
    implementation = implementation_path.name

    version_path_list = [
        version_path
        for version_path in implementation_path.iterdir()
        if version_path.is_dir()
    ]
    for version_path in version_path_list:
        client_version = version_path.name
        for protocol_path in version_path.iterdir():
            try:
                # automaton = load_automaton_from_file(protocol_path / "final.automaton")
                # with open(protocol_path / "automaton.dot", "w", encoding="utf-8") as fd:
                #     fd.write(automaton.dot())
                # with open(protocol_path / "automaton.dot", "r+") as f:
                #     # 加个入口节点
                #     lines = f.readlines()
                #     lines.insert(1, '__start0 [label="" shape="none"];\n')
                #     lines.insert(-1, '__start0 -> "0";\n')
                #     f.seek(0)
                #     f.writelines(lines)
                with open(protocol_path / "automaton.dot") as f:
                    state_machine = f.read()
            except OSError:
                continue
            protocol = protocol_path.name
            results[protocol][state_machine].append((implementation, client_version))
    return results


def prefix_nodes(graph, prefix):
    """Prefix every node of the graph with the specified prefix."""
    mapping = {node: f"{prefix}{node}" for node in graph.nodes}
    return networkx.relabel_nodes(graph, mapping)


def add_resets_edges(graph, start):
    """Add a "RESET / -" edge from every sinkhole to the start state."""
    for node in graph.nodes:
        neighbors = list(graph[node])
        if neighbors == [node]:
            graph.add_edge(node, start, label="RESET / ")


def convert_graph(graph, *, add_resets=False):
    """Convert a graph from LearnLib DOT output to dict, with the structure
    required by adg-finder.
    # """
    converted = {}

    # The first (and only) state connected to the dummy_start, is the actual
    # start state.
    dummy_start = [node for node in graph.nodes if graph.in_degree(node) == 0][0]
    converted["initial_state"] = [node for node in graph[dummy_start]][0]

    # Remove the dummy start node
    graph.remove_node(dummy_start)

    # Include a sorted list of states
    converted["states"] = sorted(graph.nodes)

    # If requested, add reset edges
    if add_resets:
        add_resets_edges(graph, converted["initial_state"])

    # Convert all transitions to tuple format
    converted["transitions"] = []
    inputs = set()
    outputs = set()
    for edge in graph.edges:
        label = graph.edges[edge]["label"]
        sent, received = (x.replace('"', "").strip() for x in label.split("/"))

        source, destination, _ = edge
        transition = [(source, sent), (received, destination)]
        converted["transitions"].append(transition)

        inputs.add(sent)
        outputs.add(received)

    converted["inputs"] = sorted(inputs)
    converted["outputs"] = sorted(outputs)

    return
