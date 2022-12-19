# 推断TLS客户端状态机
import logging
import os
import os.path
import socket
import sys
import time

from pylstar.ActiveKnowledgeBase import ActiveKnowledgeBase
from pylstar.LSTAR import LSTAR
from pylstar.Letter import Letter
from pylstar.Word import Word

import config.scenarios
from HappyPathFirst import HappyPathFirst
from StoreHypotheses import StoreHypotheses
from automata.automata import convert_from_pylstar
from src.util import tls_args
from stubs.server_concretization import InfererTools
from util.utils import fill_answer_with, get_expected_output, read_next_msg

"""
服务端与客户端交互过程：
1.客户端的容器里面会运行一个脚本，它用ncat命令监听4444端口
2.服务端连接上这个端口，并且监听4433端口
3.服务端发送信息"127.0.0.1 4433"给脚本
4.脚本收到信息后启动客户端，连接服务端（"127.0.0.1 4433"）
由于在推理过程中客户端收到错误消息会断开连接，我们需要不断重启客户端，
所以步骤3和步骤4会在推理过程中反复执行。
"""


class TLSClientKnowledgeBase(ActiveKnowledgeBase):
    def __init__(self, tls_version, options):
        super().__init__()

        if options.crypto_material.default_material() == (None, None):
            raise Exception("缺少加密套件")

        if options.trigger_endpoint:
            accept_timeout = options.timeout
        else:
            accept_timeout = None

        self.tools = InfererTools(
            options.local_endpoint,
            options.crypto_material,
            options.timeout,
            accept_timeout,
        )
        self.tls_version = tls_version
        self.broken_client = False
        self.client_trigger = None
        self.tls_session = None
        self.options = options

    def start(self):
        # 连接客户端容器中的脚本
        if self.options.trigger_endpoint:
            endpoint_tuple = self.options.trigger_endpoint.as_tuple()
            self.client_trigger = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_trigger.connect(endpoint_tuple)

        # 启动TLS服务端
        self.tls_session = self.tools.initTLS13Connexion()

    # 关闭和脚本的连接
    def stop(self):
        if self.client_trigger:
            self.client_trigger.close()

    # 脚本自动启动客户端，不需要服务端去启动
    def start_target(self):
        pass

    # 关闭和客户端的连接
    def stop_target(self):
        if self.tls_session.socket:
            self.tls_session.socket.close()

    # 通过运行在客户端的脚本来启动客户端
    # 客户端那边的容器里运行ncat命令，它作为服务端端，TLS服务端向它发送消息"127.0.0.1 4433"
    # 然后ncat将信息转发给shell命令，shell命令读取ip和port之后运行TLS客户端来连接TLS服务端
    # 每执行一次该函数就会启动一次TLS客户端
    def trigger_client(self):
        host, port = self.options.local_endpoint.as_tuple()
        trigger_string = f"{host} {port}\n".encode("utf8")
        if self.client_trigger:
            self.client_trigger.send(trigger_string)
            try:
                _ = self.client_trigger.recv(8192, socket.MSG_DONTWAIT)
            except BlockingIOError:
                pass

    # 服务端accept
    def accept_connection(self):
        try:
            self.tls_session.WAITING_CLIENT()
        except socket.timeout:
            return False

        self.tls_session.INIT_TLS_SESSION()
        if self.tls_version == "tls13":
            self.tls_session.tls13_handle_ClientHello()
        else:
            self.tls_session.tls12_handle_ClientHello()

        return True

    #
    def submit_word(self, word):
        n = len(word.letters)

        if self.broken_client:
            letters = fill_answer_with([], "NO_CONNECTION", n)
            return Word(letters=letters)

        expected_letters = get_expected_output(word, self.knowledge_tree)
        if len(expected_letters) == n:
            return Word(letters=expected_letters)

        self.trigger_client()
        if not self.accept_connection():
            self.broken_client = True
            letters = fill_answer_with([], "NO_CONNECTION", n)
            return Word(letters=letters)

        output_letters = []
        for i in range(n):
            if self.options.verbose:
                msg_to_send = "+".join(list(word.letters[i].symbols))
                self.options.log(msg_to_send)

            expected_letter = None
            if expected_letters:
                expected_letter = expected_letters.pop(0)

            output_letter = self.send_and_receive(
                expected_letter, word.letters[i].symbols
            )

            if self.options.verbose:
                self.options.log(f" => {output_letter}\n")

            output_letters.append(Letter(output_letter))
            if output_letter == "EOF":
                output_letters = fill_answer_with(output_letters, "EOF", n)
                break

        if self.options.verbose:
            self.options.log("\n")
        return Word(letters=output_letters)

    # 与客户端交互
    def send_and_receive(self, expected_output, symbols):
        try:
            self.tools.concretize_server_messages(self.tls_session, symbols)
            self.tls_session.flush_records(symbols)
        except BrokenPipeError:
            return "EOF"
        except ConnectionResetError:
            return "EOF"
        # pylint: disable=broad-except
        except Exception:
            return "INTERNAL ERROR DURING EMISSION"

        if expected_output is not None and expected_output == "No RSP":
            return "No RSP"

        try:
            response = read_next_msg(self.tls_session)
            if response is None:
                return "EOF"
            if not response:
                return "No RSP"

            while expected_output is None or expected_output != "+".join(response):
                next_msg = read_next_msg(self.tls_session)
                if not next_msg:  # Covers next_msg is None and next_msg = []
                    break
                response += next_msg
            return "+".join(response)
        # pylint: disable=broad-except
        except Exception:
            return "INTERNAL ERROR DURING RECEPTION"


def log_fn(log_file, s):
    print(s, end="")
    sys.stdout.flush()
    log_file.write(s)


def main():
    # 解析命令行参数
    args = tls_args.parse_args(client_inference=True)

    try:
        os.mkdir(args.output_dir)
    except FileExistsError:
        pass
    log_filename = f"{args.output_dir}/infer_client.log"
    log_file = open(log_filename, "w", encoding="utf-8")
    log = lambda s: log_fn(log_file, s)
    args.log = log

    dirname = os.path.dirname(sys.argv[0])
    with open(
            f"{dirname}/../scenarios/{args.vocabulary}-server.scenario",
            "r",
            encoding="utf-8",
    ) as scenario_file:
        # 以命令行参数的形式传入加密套件
        crypto_material_names = [name for name in args.crypto_material.iter_names()]
        # 加载实验场景
        scenario = config.scenarios.load_scenario(scenario_file, crypto_material_names)
    if scenario.role != "server":
        raise Exception("Invalid scenario (expecting a client role)")

    TLSBase = TLSClientKnowledgeBase(scenario.tls_version, options=args)

    logging.getLogger("WpMethodEQ").setLevel(logging.DEBUG)
    logging.getLogger("RandomWalkMethod").setLevel(logging.DEBUG)
    logging.getLogger("BDistMethod").setLevel(logging.DEBUG)
    logging.getLogger("HappyPathFirst").setLevel(logging.DEBUG)
    logging.getLogger("StoreHypotheses").setLevel(logging.DEBUG)

    try:
        TLSBase.start()

        if args.messages:
            input_sequence = Word(letters=[Letter(m) for m in args.messages])
            output_sequence = TLSBase._resolve_word(input_sequence)
            output = [list(l.symbols)[0] for l in output_sequence.letters]
            last_output = output
            repetitions = 1

            for sent, received in zip(args.messages, output):
                print(f"{sent} => {received}")
            sys.stdout.flush()

            for _i in range(1, args.loops):
                output_sequence = TLSBase._execute_word(input_sequence)
                output = [list(l.symbols)[0] for l in output_sequence.letters]

                if output == last_output:
                    repetitions += 1
                    continue

                print(f"    sequence observed {repetitions} times\n")
                repetitions = 1
                last_output = output

                for sent, received in zip(args.messages, output):
                    print(f"{sent} => {received}")
                sys.stdout.flush()

            if args.loops > 1:
                print(f"    sequence observed {repetitions} times\n")

            return

        # 将输入集转换为Letter类，一个str对应一个Letter，比如ServerHello对应一个Letter
        input_letters = [Letter(s) for s in scenario.input_vocabulary]
        log(f"input_letters {scenario.input_vocabulary}\n")
        log(f"eqtests: {args.eq_method_str}\n")
        log(f"timeout: {args.timeout}\n")

        # 等价查询
        eqtests = args.eq_method((TLSBase, input_letters))
        if not args.disable_happy_path_first and scenario.interesting_paths:
            interesting_paths_with_letters = [
                [Letter(s) for s in path] for path in scenario.interesting_paths
            ]
            eqtests = HappyPathFirst(TLSBase, interesting_paths_with_letters, eqtests)
        eqtests = StoreHypotheses(
            TLSBase,
            scenario.input_vocabulary,
            args.output_dir,
            eqtests,
        )

        # 学习过程----------------------------------
        lstar = LSTAR(
            scenario.input_vocabulary, TLSBase, max_states=15, eqtests=eqtests
        )
        start = time.time()
        state_machine = lstar.learn()
        end = time.time()

        duration = end - start
        log(f"\ntime spent in lstar.learn(): {duration}\n")
        log(f"n_states: {len(state_machine.get_states())}\n")
        # -----------------------------------------
    finally:
        TLSBase.stop()

    automaton = convert_from_pylstar(scenario.input_vocabulary, state_machine)
    with open(f"{args.output_dir}/final.automaton", "w", encoding="utf-8") as fd:
        fd.write(f"{automaton}\n")
    # with open(f"{args.output_dir}/automaton.dot", "w", encoding="utf-8") as fd:
    #     fd.write(automaton.dot())

    log(f"n_queries={TLSBase.stats.nb_query}\n")
    log(f"n_submitted_queries={TLSBase.stats.nb_submited_query}\n")
    log(f"n_letters={TLSBase.stats.nb_letter}\n")
    log(f"n_submitted_letters={TLSBase.stats.nb_submited_letter}\n")


if __name__ == "__main__":
    main()
