import json
from abc import ABC, abstractmethod


class GraphQLTracingParser:
    def parseTracings(self, input=None, **kwargs):
        result = json.loads(input)
        tracing = result["extensions"]["tracing"]
        version = tracing["version"]
        startTime = tracing["startTime"]
        endTime = tracing["endTime"]
        duration = tracing["duration"]
        parsing = tracing["parsing"]
        parsingStep = ParsingStep(parsing["startOffset"], parsing["duration"])
        validation = tracing["validation"]
        validationStep = ValidationStep(validation["startOffset"], validation["duration"])
        resolversObj = tracing["execution"]["resolvers"]
        fieldLevelResolverMap = {}

        if len(resolversObj) == 0:
            return

        rootResolver = ResolverStep(resolversObj[0]["path"], resolversObj[0]["parentType"],
                                    resolversObj[0]["fieldName"],
                                    resolversObj[0]["returnType"], resolversObj[0]["startOffset"],
                                    resolversObj[0]["duration"])
        fieldLevelResolverMap[0, rootResolver.getFieldName()] = rootResolver

        for i in range(1, len(resolversObj)):
            resolver = ResolverStep(resolversObj[i]["path"], resolversObj[i]["parentType"],
                                    resolversObj[i]["fieldName"],
                                    resolversObj[i]["returnType"], resolversObj[i]["startOffset"],
                                    resolversObj[i]["duration"])

            fieldLevelResolverMap[resolver.getPathLen() - 1, resolver.getFieldName()] = resolver
            parentLevel, parentField = resolver.getParentFieldLevel()
            parentResolver = fieldLevelResolverMap[(parentLevel, parentField)]
            parentResolver.appendChild(resolver)

        execution = QueryExecution(version, startTime, endTime, duration, parsingStep, validationStep,
                                   ResolverExecutionTree(rootResolver, duration - (
                                           parsingStep.getDuration() + validationStep.getDuration())))

        return execution


class Step(ABC):
    def __init__(self, startOffset, duration):
        self.startOffset = startOffset
        self.duration = duration

    @abstractmethod
    def getStepName(self):
        pass

    def getDuration(self):
        return self.duration

    def getStartOffset(self):
        return self.startOffset


class ParsingStep(Step, ABC):
    def __init__(self, startOffset, duration):
        super().__init__(startOffset, duration)

    def getStepName(self):
        return "Parsing duration " + str(self.duration)


class ValidationStep(Step, ABC):
    def __init__(self, startOffset, duration):
        super().__init__(startOffset, duration)

    def getStepName(self):
        return "Validation duration " + str(self.duration)


class ResolverStep(Step, ABC):
    def __init__(self, path, parentType, fieldName, returnType, startOffset, duration):
        super().__init__(startOffset, duration)
        self.path = path
        self.parentType = parentType
        self.fieldName = fieldName
        self.returnType = returnType
        self.children = set()

    def getStepName(self):
        result = self.getUniqueResolverName() + " Resolver duration " + str(self.duration)
        for child in self.children:
            result += "\n" + child.getStepName()

        return result

    def getUniqueResolverName(self):
        resolverName = self.path[0]
        for i in range(1, len(self.path)):
            resolverName += "/" + str(self.path[i])
        return resolverName

    def getPathLen(self):
        return len(self.path)

    def getFieldName(self):
        return self.fieldName

    def getParentFieldLevel(self):
        pathLen = self.getPathLen()
        if pathLen < 2:
            return 0, None

        lenParent = pathLen - 2
        parent = self.path[lenParent]
        if isinstance(parent, int):
            lenParent = lenParent - 1
            parent = self.path[lenParent]

        return lenParent, parent

    def appendChild(self, child):
        self.children.add(child)

    def getChildren(self):
        return self.children


class ResolverExecutionTree(Step, ABC):
    def __init__(self, resolverTree, duration):
        self.resolverTree = resolverTree
        self.duration = duration

    def getStepName(self):
        return "Execution duration " + str(self.duration) + "\n" + self.resolverTree.getStepName()

    def getStartOffset(self):
        return self.resolverTree.getStartOffset()

    def getResolverTree(self):
        return self.resolverTree

class QueryExecution(Step, ABC):
    def __init__(self, version, startTime, endTime, duration, parsing, validation, resolverExecution):
        super().__init__(0, duration)
        self.version = version
        self.startTime = startTime
        self.endTime = endTime
        self.parsing = parsing
        self.validation = validation
        self.resolverExecution = resolverExecution

    def getStepName(self):
        return "Query Execution duration: " + str(
            self.duration) + " start time: " + self.startTime + " end time: " + self.endTime + "\n" \
               + self.parsing.getStepName() + " \n" + self.validation.getStepName() + "\n" + self.resolverExecution.getStepName()

    def getParsingStep(self):
        return self.parsing

    def getValidationStep(self):
        return self.validation

    def getResolverExecution(self):
        return self.resolverExecution

    def getVersion(self):
        return self.version

    def getStartTime(self):
        return self.startTime

    def getEndTime(self):
        return self.endTime
