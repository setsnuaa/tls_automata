# tls_automata

本仓库用于保存毕业论文代码。

目录结构：/src是指纹识别的代码，/scenarios是不同TLS版本的输入字符集，/tls_test是实验代码。

/tls_test/stacks下保存了各个版本的实现。

## 使用说明

我们作为服务端去和客户端交互，那么首先需要配置服务端的SSL证书，然后创建服务端的容器、推理工具的容器，最后运行实验脚本。

来到/tls_test目录下，里面有个Makefile，所有命令都写好了，

- 生成服务端证书：`make crypto-material`
- 生成客户端容器，比如我们想用openssl-3.0.0，`make containers/openssl/openssl-3.0.2.docker`，注意make命令的名称格式为containers/大版本/小版本，然后在containers/openssl/openssl-3.0.2.docker这个文件里面会保存镜像id。注：stacks/openssl*/tags下面是目前收集的客户端版本。
- 生成推理工具容器，`make containers/tool/tls-inferer.docker`，同样可以在containers/tool/tls-inferer.docker文件里面找到镜像id
- 运行实验脚本，`./infer-client.sh tls-test/openssl:openssl-3.0.0 1.3 tls13`，推理工具会对openssl-3.0.0客户端指纹识别，1.3是客户端的tls版本，tls13是推理工具的实验场景，两个要对应，比如想对tls1.2指纹识别，那么客户端对应1.2，推理工具对应tls12
- 简化状态机，`./automaton2dot.py client.[tls13/tls12] final.automaton final.dot`
- 绘制状态机，`dot -Tpdf input.dot -o output.pdf`

生成的状态机保存在/tls_test/results下面。
