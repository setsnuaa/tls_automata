# TLS信息抽象类
from typing import List, Dict, Tuple, Optional
import socket

from pylstar.Letter import Letter
from pylstar.Word import Word
from pylstar.KnowledgeTree import KnowledgeTree

from scapy.layers.tls.record import TLSAlert, _tls_alert_description


class Endpoint:
    def __int__(self, endpoint_str: str):
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


class CryptoMaterial:
    def __int__(self):
        self.material: Dict[str, Tuple[str, str]] = {}
        self.default_cert: Optional[str] = None

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
