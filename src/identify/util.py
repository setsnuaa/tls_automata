# -*- coding：utf-8 -*-
from collections import defaultdict
from pathlib import Path
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
                with open(protocol_path / "automaton.dot") as f:
                    # 加个入口节点
                    # TODO
                    state_machine = f.read()
            except OSError:
                continue
            protocol = protocol_path.name
            results[protocol][state_machine].append((implementation, client_version))
    return results
