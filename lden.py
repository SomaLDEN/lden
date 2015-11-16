#!/usr/bin/python
# coding=utf-8

from src.python.evtmanage import EventManager
from src.python.all_event import AllEvent
from src.python.ldenparse import LdenParser
from src.python.condexprparse import ConditionExpressionParser
from src.python.mapread import MapReader
from bcc import BPF
from time import sleep
from sys import argv, maxint
import os

## DEFINE CONSTANT & DECLARE GLOBAL VARIABLE ##
INTERVAL = 0.5
MAP = "map"
task_dict = {}
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

def dfs_parse_tree(tree):
    flag = False
    if len(tree) == 3:
        flag = dfs_parse_tree(tree[1])
        if tree[0] == 1:
            return flag and dfs_parse_tree(tree[2])
        else:
            return flag or dfs_parse_tree(tree[2])
    else:
        while len(tree) != 3:
            tree = tree[0]
        left = 0
        right = 0
        if len(tree[1]) > 1:
            left = task_dict[tree[1][0]][1][tree[1][1]]
        else:
            left = int(tree[1][0])

        if len(tree[2]) > 1:
            right = task_dict[tree[2][0]][1][tree[2][1]]
        else:
            right = int(tree[2][0])

        if tree[0] == ">=":
            return left >= right
        elif tree[0] == "<=":
            return left <= right
        elif tree[0] == ">":
            return left > right
        elif tree[0] == "<":
            return left < right
        elif tree[0] == "=":
            return left == right
        else:
            return left != right


if __name__ == "__main__":
    argv_parser = LdenParser(argv)
    commander = argv_parser.result[0]
    user_args = argv_parser.result[1]


    ##############################
    # "all" command executed
    if commander == 0:
        visualizer = AllEvent(ipaddress=user_args["address"], port=user_args["port"])
        try:
            visualizer.main_run()
        except KeyboardInterrupt:
            print ""
            pass
    # "all" command ended
    ##############################


    ##############################
    # "notify" command executed
    else:
        manager = EventManager()

        ## parsing expression
        condexpr_parser = ConditionExpressionParser()
        (event_parse_tree, chosen_event) = condexpr_parser.parse(user_args["expression"])
        ## ## ## ## ## ## ##

        ## attach kprobe
        for k in chosen_event.keys():
            code_and_func = manager.EVENT_LIST[k]
            b = BPF(text=code_and_func[0])

            if len(code_and_func) > 2:
                for func_idx in range(1, len(code_and_func)):
                    if (func_idx & 1) == 0:
                        continue
                    b.attach_kprobe(event=code_and_func[func_idx],
                            fn_name=code_and_func[func_idx + 1])
            else:
                b.attach_kprobe(event=code_and_func[1], fn_name='func')

            task_dict[k] = [MapReader(b, MAP), None]
        ## ## ## ## ## ## ##

        ## read maps until timeout
        if user_args["time"] is None:
            timeout = maxint
        else:
            try:
                timeout = float(user_args["time"])
            except:
                print "Invalid time \'",  str(timeout), "\'. Value of option \'time\' must be integer type or float type."
                exit()

        sleep(1)

        print "# Tracing selected events..."
        print "# Condition : ", user_args["expression"]
        print "# Timeout   : ", "infinity" if timeout is maxint else str(timeout) + " s"
        print "# Script    : ", user_args["script"]

        try:
            sleep_time = 0
            while True:
                if (sleep_time >= timeout):
                    print "timeout"
                    exit()
                sleep_time += INTERVAL
                sleep(INTERVAL)

                for k, v in task_dict.items():
                    v[1] = v[0].read_map()

                if dfs_parse_tree(event_parse_tree):
                    print "EVENT!"
                    if user_args["script"] is not None:
                        os.system(user_args["script"])
                    exit()

        except KeyboardInterrupt:
            print ""
            exit()
        ## ## ## ## ## ## ##

    # "notify" command ended
    ##############################

