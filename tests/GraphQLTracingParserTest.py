import json
from unittest import TestCase

from GraphQLExplainer import GraphQLExplainer
from Parser.GraphQLTracingParser import GraphQLTracingParser


class GraphQLTracingParserTest(TestCase):

    def setUp(self) -> None:
        self.tracing = {
            "data": {
                "hero": {
                    "name": "R2-D2",
                    "friends": [
                        {
                            "name": "Luke Skywalker"
                        },
                        {
                            "name": "Han Solo"
                        },
                        {
                            "name": "Leia Organa"
                        }
                    ]
                }
            },
            "extensions": {
                "tracing": {
                    "version": 1,
                    "startTime": "2017-07-28T14:20:32.106Z",
                    "endTime": "2017-07-28T14:20:32.109Z",
                    "duration": 2694443,
                    "parsing": {
                        "startOffset": 34953,
                        "duration": 351736,
                    },
                    "validation": {
                        "startOffset": 412349,
                        "duration": 670107,
                    },
                    "execution": {
                        "resolvers": [
                            {
                                "path": [
                                    "hero"
                                ],
                                "parentType": "Query",
                                "fieldName": "hero",
                                "returnType": "Character",
                                "startOffset": 1172456,
                                "duration": 215657
                            },
                            {
                                "path": [
                                    "hero",
                                    "name"
                                ],
                                "parentType": "Droid",
                                "fieldName": "name",
                                "returnType": "String!",
                                "startOffset": 1903307,
                                "duration": 73098
                            },
                            {
                                "path": [
                                    "hero",
                                    "friends"
                                ],
                                "parentType": "Droid",
                                "fieldName": "friends",
                                "returnType": "[Character]",
                                "startOffset": 1992644,
                                "duration": 522178
                            },
                            {
                                "path": [
                                    "hero",
                                    "friends",
                                    0,
                                    "name"
                                ],
                                "parentType": "Human",
                                "fieldName": "name",
                                "returnType": "String!",
                                "startOffset": 2445097,
                                "duration": 18902
                            },
                            {
                                "path": [
                                    "hero",
                                    "friends",
                                    1,
                                    "name"
                                ],
                                "parentType": "Human",
                                "fieldName": "name",
                                "returnType": "String!",
                                "startOffset": 2488750,
                                "duration": 2141
                            },
                            {
                                "path": [
                                    "hero",
                                    "friends",
                                    2,
                                    "name"
                                ],
                                "parentType": "Human",
                                "fieldName": "name",
                                "returnType": "String!",
                                "startOffset": 2501461,
                                "duration": 1657
                            }
                        ]
                    }
                }
            }
        }

    def testParser(self):
        parser = GraphQLTracingParser()
        execution = parser.parseTracings(json.dumps(self.tracing))
        self.assertEqual(execution.getVersion(), 1)
        self.assertEqual(execution.getStartTime(), "2017-07-28T14:20:32.106Z")
        self.assertEqual(execution.getEndTime(), "2017-07-28T14:20:32.109Z")

        parsing = execution.getParsingStep()
        self.assertEqual(parsing.getStartOffset(), 34953)
        self.assertEqual(parsing.getDuration(), 351736)

        validation = execution.getValidationStep()
        self.assertEqual(validation.getStartOffset(), 412349)
        self.assertEqual(validation.getDuration(), 670107)

        resolverTree = execution.getResolverExecution().getResolverTree()
        self.assertEqual(resolverTree.getStartOffset(),  1172456)
        self.assertEqual(resolverTree.getDuration(), 215657)
        self.assertEqual(len(resolverTree.getChildren()), 2)
        GraphQLExplainer().explain(json.dumps(self.tracing))