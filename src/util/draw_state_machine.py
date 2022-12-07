import graphviz


filepath="D:\learnedModel.dot"
with open(filepath) as dot_file:
    dot_graph=dot_file.read()
graph=graphviz.Source(dot_graph)
graph.view()

