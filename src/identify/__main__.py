# -*- coding：utf-8 -*-
import src.identify.command as cm

if __name__ == "__main__":
    # 去重
    # cm.dedup_command("D:\\code0\\tls_automata_results\\state_machine",
    #                  "D:\\code0\\tls_automata_results\\dedup")
    # 构建状态树
    # cm.learn_command("D:\\code0\\tls_automata_results\\dedup\\TLS12",
    #                  "D:\\code0\\tls_automata_results\\data\\TLS12.p","hdt")
    # 状态树可视化
    # cm.draw("D:\\code0\\tls_automata_results\\data\\TLS12.p",
    #         "D:\\code0\\tls_automata_results\\picture\\tree.svg")
    # 测试
    cm.benchmark_command("D:\\code0\\tls_automata_results\\benchmark\\tls12_test.json")
