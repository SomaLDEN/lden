from bcc import BPF
from exprparse import *
import time
import sys
import argparse
import os
import multiprocessing
from event_function import *

EVENT_LIST = {
        "task.create" : task_create(),
        "task.exec" : task_exec(),
        "task.exit" : task_exit(),
        "task.switch" : task_switch(),
        "memory.alloc" : memory_alloc(),
        "memory.free" : memory_free(),
        "memory.alloc_page" : memory_alloc_page(),
        #"memory.free_page" : ["memory/memory_free_page.c", "__free_pages_ok", "memory_free_page_begin", "memory_free_page", "free_hot_cold_page", "memory_free_page_order_zero_begin"],
        "memory.reclaim" : memroy_reclaim(),
        "fs.pagecache_access" : fs_pagecache_access(),
        "fs.pagecache_miss" : fs_pagecache_miss(),
        "fs.read_ahead" : fs_read_ahead(),
        "fs.page_writeback_bg" : fs_page_writeback_bg(),
        "fs.page_writeback_per_inode" : fs_page_writeback_per_inode(),
        "network.tcp_send" : network_tcp_send(),
        "network.tcp_recv" : network_tcp_recv(),
        "network.udp_send" : network_udp_send(),
        "network.udp_recv" : network_udp_recv(),
        }

FUNC_LIST = {
        "count" : "cnt",
        "size" : "siz",
        "speed" : "spd"
        }

args_parser = argparse.ArgumentParser(description = "Notifier usage\nex) sudo python tester.py --expr \"count(task.switch) > 10\" --time 10 --script \"bash script.sh\"")
args_parser.add_argument("--expr", type=str, default=None, help = "the kind of event that you want notify")
args_parser.add_argument("--time", type=int, default=5, help = "timeout second")
args_parser.add_argument("--script", type=str, default=None, help = "the script to be executed after event happens")
args_result = args_parser.parse_args()

if args_result.expr:
    expr = args_result.expr
    print ("event: %s" % (expr))
if args_result.time:
    interval = args_result.time
    print ("timeout: %u" % (interval))
if args_result.script:
    shscript = args_result.script
    print ("script: %s" % (shscript))

expr_parser = ExpressionParser(operators=["<=", ">=", "=", ">", "<", "<>"])

for k, v in FUNC_LIST.items():
    expr_parser.add_functionToken(k)

for k, v in EVENT_LIST.items():
    expr_parser.add_parameterToken(k)

expr_result = expr_parser.parse_expr(expression=expr)

event_type = [None, None]
event_name = None
event_measure = None
for i in range(1,3):
    if len(expr_result[i]) == 1:
        event_type[i -1] = 1 #constant
        event_bound = expr_result[i][0]
    else:
        event_type[i - 1] = 0 #function
        event_name = expr_result[i][0]
        event_measure = FUNC_LIST[expr_result[i][1]]


def print_map():
    print ("-------------------")
    map_name = 'map'
    i = 0;
    for k,v in b[map_name].items():
        if i == 1:
            print("speed per sec : %u" %(v.count))
            return

        print ("total count : %u" % (v.count))
        i= i+1
        try:
            print ("total size : %u" % (v.size))
        except:
            pass

flag = False
def call_back (pid, call_chain):
    global flag
    if flag is False:
        flag = True
        print ("-------------------")
        os.system(shscript)
    #for idx in call_chain:
    #    print(b.ksym(idx))
    #b.trace_print()

if len(sys.argv) == 1:
    print " "
    exit()

if (event_type[0] | event_type[1]) != 1:
    call_back()
else:
    if event_type [0] == 0:
        rep_str = event_measure + expr_result[0] + event_bound
    else:
        rep_str = event_bound + expr_result[0] + event_measure
    
    rep = "EXPRESSION"
    (cfile, event_name) = EVENT_LIST[event_name]
    bpf_code = cfile.replace(rep, rep_str)

    b = BPF(text = bpf_code, cb = call_back, debug=0)

    #b.attach_kprobe(event_re="(__free_pages_ok|free_hot_cold_page)", fn_name=memory_free_page_order_zero )

    for i in range(0, multiprocessing.cpu_count()):
        b.attach_kprobe(event = event_name, fn_name = 'func', cpu=i)

    interval = interval * 1000
    b.kprobe_poll(timeout = interval)



print_map()

exit()
