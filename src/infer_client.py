# 推断TLS客户端状态机
import os
import os.path
import sys
import time
import socket
import logging

from pylstar.LSTAR import LSTAR
from pylstar.ActiveKnowledgeBase import ActiveKnowledgeBase
from pylstar.Letter import Letter
from pylstar.Word import Word

import config.scenarios
import util.tls_args
from util.utils import fill_answer_with, get_expected_output, read_next_msg
from HappyPathFirst import HappyPathFirst
from automata.automata import convert_from_pylstar
from StoreHypotheses import StoreHypotheses
from stubs.server_concretization import InfererTools


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
        if self.options.trigger_endpoint:
            endpoint_tuple = self.options.trigger_endpoint.as_tuple()
            self.client_trigger = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_trigger.connect(endpoint_tuple)

        # 启动TLS服务端
        self.tls_session = self.tools.initTLS13Connexion()

    def stop(self):
        if self.client_trigger:
            self.client_trigger.close()

    def start_target(self):
        pass

    # 关闭客户端
    def stop_target(self):
        if self.tls_session.socket:
            self.tls_session.socket.close()

    # 通过运行在客户端的脚本来启动客户端
    def trigger_client(self):
        host, port = self.options.local_endpoint.as_tuple()
        trigger_string = f"{host} {port}\n".encode("utf8")
        if self.client_trigger:
            self.client_trigger.send(trigger_string)
            try:
                _ = self.client_trigger.recv(8192, socket.MSG_DONTWAIT)
            except BlockingIOError:
                pass

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
