FROM python:3.10-buster

WORKDIR /root

RUN git clone https://github.com/setsnuaa/tls_automata.git

RUN pip install -r tls_automata/requirements.txt

COPY probe_client.sh /