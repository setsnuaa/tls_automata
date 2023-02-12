# -*- coding：utf-8 -*-
from identify.util import dedup_state_machine_dir


def main():
    # results = [tls版本,[状态机,客户端版本]]
    results = dedup_state_machine_dir("../../../tls_automata_results/state_machine")
    for protocol, state_machine_dicts in results.items():
        print("=====")
        print("TLS版本：" + protocol + ";指纹数量：" + str(len(state_machine_dicts)))
        for _, version_list in state_machine_dicts.items():
            print(version_list)
        print("=====")


if __name__ == "__main__":
    main()
