# TLS推理工具代码复用
import sys
import argparse

from pylstar.eqtests.RandomWalkMethod import RandomWalkMethod
from pylstar.eqtests.WpMethodEQ import WpMethodEQ

from utils import Endpoint, CryptoMaterial, InvalidCryptoMaterialLine


def handle_endpoint(parser, endpoint_str) -> Endpoint:
    endpoint = Endpoint(endpoint_str)
    if not endpoint.check():
        print(f'无法解析 {endpoint}', file=sys.stderr)
        parser.print_usage(file=sys.stderr)
        sys.exit(1)
    return endpoint


# 加密信息
def handle_crypto_material(parser, crypto_material_list):
    crypto_material = CryptoMaterial()

    for line in crypto_material_list:
        try:
            crypto_material.add(line)
        except InvalidCryptoMaterialLine:
            print("加密信息格式应为 name:cert:key:[:DEFAULT]", file=sys.stderr)
            parser.print_usage(file=sys.stderr)
            sys.exit(1)

    return crypto_material


# 等价查询
def handle_eq_method(parser, eq_method_str):
    msg = eq_method_str.split(":")
    if len(msg) == 2 and msg[0] == "WP":
        max_states = int(msg[1])
        return lambda x: WpMethodEQ(x[0], max_states, x[1]), f"WPMethod({max_states})"
    if len(msg) == 3 and msg[0] == "RW":
        max_steps, restart_probability = int(msg[1]), float(msg[2])
        return lambda x: RandomWalkMethod(x[0], x[1], max_steps,
                                          restart_probability), f"RandomWalkMethod({max_steps, restart_probability})"
    print(f"非法等价查询方法 ({eq_method_str})", file=sys.stderr)
    parser.print_usage(file=sys.stderr)
    sys.exit(1)


# 参数设置
def parse_args(client_inference):
    parser = argparse.ArgumentParser(
        description="Infer the mealy machine of a TLS Client."
    )

    # dest=参数名称
    parser.add_argument(
        "-T",
        "--trigger-endpoint",
        action="store",
        type=str,
        dest="trigger_endpoint_str",
        default=None,
        help="address of the trigger (default is None)",
    )

    if client_inference:
        parser.add_argument(
            "-L",
            "--local-endpoint",
            action="store",
            type=str,
            dest="local_endpoint_str",
            default="127.0.0.1:4433",
            help="address used to accept connections (default is 127.0.0.1:4433)",
        )
    else:
        parser.add_argument(
            "-R",
            "--remote-endpoint",
            action="store",
            type=str,
            dest="remote_endpoint_str",
            default="127.0.0.1:4433",
            help="address to connect to (default is 127.0.0.1:4433)",
        )

    # 加密证书配置
    parser.add_argument(
        "-C",
        "--crypto-material",
        action="append",
        dest="crypto_material_list",
        help="crypto material name:certificate:key[:default]",
        default=[],
    )

    # 超时重置
    parser.add_argument(
        "--timeout",
        action="store",
        type=float,
        dest="timeout",
        default=1.0,
        help="the timeout in seconds to use for network communications (default is 1)",
    )

    parser.add_argument(
        "--expected-minimal-timeout",
        action="store",
        type=float,
        dest="expected_minimal_timeout",
        default=0.0,
        help="always wait a minimal timeout even with the expected optimization (default is 0)",
    )

    # 默认等价查询方法
    default_eq_test = "BDist:3"
    parser.add_argument(
        "-E",
        "--eq-method",
        action="store",
        type=str,
        dest="eq_method_str",
        default=default_eq_test,
        help=f"equivalence method [WP:<states> or RW:<steps>:<reset_proba>] (default is {default_eq_test})",
    )

    parser.add_argument(
        "--disable-happy-path-first",
        action="store_true",
        dest="disable_happy_path_first",
        default=False,
    )

    # 状态机存储路径
    parser.add_argument(
        "-o",
        "--output-dir",
        action="store",
        type=str,
        dest="output_dir",
        default="/tmp/tls-inferer",
        help="output directory where to write the state machines (default is /tmp/tls-inferer)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        default=False,
        help="activate debug messages",
    )

    # TLS版本
    parser.add_argument(
        "-S",
        "--scenario",
        action="store",
        type=str,
        dest="scenario",
        default="tls12",
        help="the scenario used (default is tls12)",
    )

    parser.add_argument(
        "--loops",
        action="store",
        type=int,
        dest="loops",
        default=1,
        help="the number of times to send the messages (default is 1)",
    )

    parser.add_argument(
        "messages", metavar="messages", nargs="*", help="Sequence of messages to send"
    )

    # 解析命令行参数
    args = parser.parse_args()

    # 将解析结果保存到result
    result = argparse.Namespace()
    result.output_dir = args.output_dir
    result.verbose = args.verbose
    result.loops = args.loops
    result.messages = args.messages
    result.timeout = args.timeout
    result.expected_minimal_timeout = args.expected_minimal_timeout

    if args.trigger_endpoint_str:
        result.trigger_endpoint = handle_endpoint(parser, args.trigger_endpoint_str)
    else:
        result.trigger_endpoint = None

    if client_inference:
        result.local_endpoint = handle_endpoint(parser, args.local_endpoint_str)
    else:
        result.remote_endpoint = handle_endpoint(parser, args.remote_endpoint_str)

    result.crypto_material = handle_crypto_material(parser, args.crypto_material_list)

    result.disable_happy_path_first = args.disable_happy_path_first
    result.eq_method, result.eq_method_str = handle_eq_method(
        parser, args.eq_method_str
    )

    # Scenario = vocabulary + TLS version + Ciphersuites + Cert required?
    result.vocabulary = args.scenario

    return result
