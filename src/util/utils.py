# TLS信息抽象类
from typing import List, Dict, Tuple, Optional
import socket

from pylstar.Letter import Letter
from pylstar.Word import Word
from pylstar.KnowledgeTree import KnowledgeTree

from scapy.layers.tls.record import TLSAlert, _tls_alert_description


class Endpoint:
    def __init__(self, endpoint_str: str):
        self._host, port_str = endpoint_str.split(":")
        self._port = int(port_str)

    # 判断ip端口合法性
    def check(self) -> bool:
        try:
            socket.getaddrinfo(self._host, self._port)
            return True
        except socket.gaierror:
            return False

    def __str__(self):
        return f"{self._host}:{self._port}"

    def as_tuple(self):
        return self._host, self._port


class InvalidCryptoMaterialLine(BaseException):
    pass


# 证书配置类，由于我们要作为服务端去推测客户端，因此需要我们自己生成服务端证书和私钥
class CryptoMaterial:
    def __init__(self):
        self.material: Dict[str, Tuple[str, str]] = {}
        self.default_cert: Optional[str] = None

    # 添加证书信息 格式为 name:cert:key:default_cert
    def add(self, arg_line):
        msg = arg_line.split(":")
        if len(msg) == 3:
            msg.append(False)
        elif len(msg) == 4 and msg[3] == "DEFAULT":
            msg[3] = True
        else:
            raise InvalidCryptoMaterialLine

        name, cert, key, default_cert = msg
        self.material[name] = (cert, key)
        if default_cert:
            self.default_cert = name

    def iter_names(self):
        for name in self.material:
            yield name

    def iter_non_default_names(self):
        for name in self.material:
            if name != self.default_cert:
                yield name

    def default_material(self) -> Tuple[Optional[str], Optional[str]]:
        if self.default_cert:
            return self.material[self.default_cert]
        return None, None

    def get_material(self, name: str) -> Tuple[str, str]:
        return self.material[name]

    def __nonzero__(self):
        return bool(self.material)


def abstract_alert_message(alert: TLSAlert):
    if alert.level == 1:
        alert_level = "Warning"
    elif alert.level == 2:
        alert_level = "FatalAlert"
    else:
        return "UnknownPacket"
    try:
        return f"{alert_level}({_tls_alert_description[alert.descr]})"
    except KeyError:
        return "UnknownPacket"


def abstract_response(responses):
    msg_type = []
    for response in responses:
        try:
            # TLS信息里面如果存在Load字段，代表scapy不能解析该字段
            # 如果不存在，抛出"AttributeError"错误，接着执行后面的语句
            _ = response.load
            msg_type.append("UnknownPacket")
            continue
        except AttributeError:
            pass
        if isinstance(response, TLSAlert):
            msg_type.append(abstract_alert_message(response))
        else:
            # 判断TLS消息的类型，这里的类型类似于<class 'scapy.plist.PacketList'>
            # 需要先处理一下这个字符串，只有后缀PacketList有用
            abstract_msg = str(type(response)).rsplit(".", maxsplit=1)[-1].replace("'>", "")
            if abstract_msg == "Raw":
                abstract_msg == "UnknownPacket"
            elif abstract_msg == "TLSApplicationData":
                # 在scapy可能会把一些信息错误的解析为TLSApplicationData，需要判断一下
                try:
                    response.data.decode("utf-8")
                except UnicodeDecodeError:
                    abstract_msg = "UnknownPacket"
            msg_type.append(abstract_msg)
        if "UnknownPacket" in msg_type:
            return ["UnknownPacket"]

    return msg_type


# ？
def fill_answer_with(prefix: List[Letter], symbol: str, length: int) -> List[Letter]:
    letters = prefix
    while len(letters) < length:
        letters.append(Letter(symbol))
    return letters


# ？
def get_expected_output(input_word: Word, knowledge_tree: KnowledgeTree) -> List[Letter]:
    prefix = input_word.letters[:-1]
    while prefix:
        try:
            prefix_word = Word(letters=prefix)
            output_prefix = knowledge_tree.get_output_word(prefix_word).letters
            expected_output_word = [letter.name.strip("'") for letter in output_prefix]
            if expected_output_word[-1] == "EOF":
                return fill_answer_with(output_prefix, "EOF", len(input_word.letters))
            return expected_output_word
        except Exception:
            prefix.pop()
    return []


def read_next_msg(tls_session, timeout=None):
    try:
        if timeout:
            # 调用这个函数后客户端发送的消息存到服务端的缓存里面了
            tls_session.get_next_msg(socket_timeout=timeout)
        else:
            tls_session.get_next_msg()
    except socket.timeout:
        return []
    except ConnectionResetError:
        return None
    except BrokenPipeError:
        return None
    if not tls_session.buffer_in:
        return None
    # 将实际信息转换为抽象信息
    result = abstract_response(tls_session.buffer_in)
    tls_session.buffer_in = []
    return result
