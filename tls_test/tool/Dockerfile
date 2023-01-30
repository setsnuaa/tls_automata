FROM python:3.10-buster

WORKDIR /root

RUN git clone https://hub.nuaa.cf/setsnuaa/tls_automata.git
#RUN git clone https://github.com/setsnuaa/tls_automata.git

RUN pip install -r tls_automata/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY probe_client.sh /
