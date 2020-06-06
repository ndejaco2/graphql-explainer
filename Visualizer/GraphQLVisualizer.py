import plotly.figure_factory as ff

class GraphQLVisualizer:
    def visualize(self, input=None):

        parsingStep = input.getParsingStep()
        validationStep = input.getValidationStep()
        executionStep = input.getExecutionStep()

        df = [dict(Task="Parsing", Start=str(parsingStep.getStartOffset()),
                   Finish=str(parsingStep.getDuration() + parsingStep.getStartOffset()), Resource='Parsing'),
              dict(Task="Validation", Start=str(validationStep.getStartOffset()),
                   Finish=str(validationStep.getDuration() + parsingStep.getStartOffset()), Resource='Validation')]

        resolvers = [executionStep.getResolverTree()]
        while len(resolvers) > 0:
            resolver = resolvers.pop()
            resolverName = resolver.getUniqueResolverName() + ' Resolver'
            df.append(dict(Task=resolverName, Start=str(resolver.getStartOffset()),
                   Finish=str(resolver.getDuration() + resolver.getStartOffset()),
                   Resource=resolverName))

            for child in resolver.getChildren():
                resolvers.append(child)

        fig = ff.create_gantt(df, index_col='Resource', reverse_colors=True,
                              show_colorbar=True, group_tasks=True, showgrid_x=False, title='Query Execution Breakdown in Nanoseconds')

        fig.layout.xaxis.rangeselector = None
        fig['layout']['xaxis'].update({'type': None})
        fig.show()