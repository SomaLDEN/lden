# coding=utf-8

from parser.condparse import ConditionParser
from parser.exprparse import ExpressionParser
from evtmanage import EventManager

class ConditionExpressionParser:

    def __init__(self):
        self.result = []
        self.event_list = {}
        self.cond_parser = ConditionParser()
        self.expr_parser = ExpressionParser([">=", "<=", ">", "<", "=", "<>"])

        self.cond_parser.add_and_operator(" and ")
        self.cond_parser.add_and_operator("&")
        self.cond_parser.add_or_operator(" or ")
        self.cond_parser.add_or_operator("|")

        self.expr_parser.add_function_token("count")
        self.expr_parser.add_function_token("size")
        self.expr_parser.add_function_token("speed")

        self.manager = EventManager()
        for k in self.manager.EVENT_LIST.keys():
            self.expr_parser.add_parameter_token(k)
        self.expr_parser.add_parameter_token("custom")

    def parse(self, condexpr):
        self.result = self.cond_parser.parse_cond(condexpr)
        self.recursive_split(self.result)
        return self.result, self.event_list

    def recursive_split(self, recursive_list):
        if len(recursive_list) == 1:
            while (type(recursive_list[0]) is str) is False:
                recursive_list = recursive_list[0]
            recursive_list[0] = self.expr_parser.parse_expr(recursive_list[0])

            for i in range(1,3):
                if len(recursive_list[0][i]) > 2:
                    print "Syntax error"
                    exit()
                if len(recursive_list[0][i]) > 1:
                    if recursive_list[0][i][0] not in self.manager.SIZE_EVENT and recursive_list[0][i][1] == "size":
                        print "Event \'" + recursive_list[0][i][0] + "\' cannot get size data."
                        exit()
                    if recursive_list[0][i][0] not in self.event_list:
                        self.event_list[recursive_list[0][i][0]] = None
        else:
            self.recursive_split(recursive_list[1])
            self.recursive_split(recursive_list[2])
