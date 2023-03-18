# -*- coding：utf-8 -*-
import json
import pickle
from pathlib import Path

from . import util
from .benchmark import benchmark_all
from .benchmark import visualize_all
from .learn import _dot_to_networkx
from .learn import construct_tree_from_dedup


# 去重
def dedup_command(state_machine_directory, output_directory):
    results = util.dedup_state_machine_dir(state_machine_directory)
    output_path = Path(output_directory)
    for protocol, models in results.items():
        for index, (model, versions) in enumerate(models.items()):
            model_name = f"model-{index + 1}"
            model_dir = output_path / protocol / model_name

            # Create the directory
            model_dir.mkdir(parents=True, exist_ok=True)

            # Write the model to this directory, both in Graphviz and JSON
            # format.
            with open(model_dir / "model.gv", "w") as f:
                f.write(model)

            graph = _dot_to_networkx(model)
            graph = util.prefix_nodes(graph, f"{model_name}_")
            converted = util.convert_graph(graph, add_resets=True)
            with open(model_dir / "model.json", "w") as f:
                json.dump(converted, f, indent=4)

            # Add the version list
            with open(model_dir / "versions.json", "w") as f:
                json.dump(versions, f, indent=4)


# 构建状态树
def learn_command(dedup_directory, output_file, tree_type):
    tree = construct_tree_from_dedup(dedup_directory, tree_type=tree_type)
    with open(output_file, "wb") as output:
        pickle.dump(tree, output)


# 测试
def benchmark_command(output_file):
    results = benchmark_all()
    with open(output_file,"w") as output:
        json.dump(results, output, indent=4)


# 实验结果可视化
def benchmark_visualize_command(benchmark_file, output_directory):
    visualize_all(json.load(benchmark_file), output_directory)


# 状态树可视化
def draw(graph_dir, output_dir):
    with open(graph_dir, "rb") as graph:
        hdt = pickle.load(graph)
    result = hdt.draw("svg")
    with open(output_dir, "wb") as output:
        output.write(result)
