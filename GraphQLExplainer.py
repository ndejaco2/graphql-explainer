from Parser.GraphQLTracingParser import GraphQLTracingParser
from Visualizer.GraphQLVisualizer import GraphQLVisualizer

class GraphQLExplainer:

    def __init__(self, debug=False, **kwargs):
        self.parser = GraphQLTracingParser()
        self.vizualizer = GraphQLVisualizer()

    def explain(self, input=None, **kwargs):
        execution = self.parser.parseTracings(input)
        self.vizualizer.visualize(execution)


