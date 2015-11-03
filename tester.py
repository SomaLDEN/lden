from bcc import BPF
import time
import sys
import argparse
import os

parser = argparse.ArgumentParser(description = "Notifier usage\nex) sudo python tester.py --event task.create --condition \"count > 1\" --time 10 --script \"bash script.sh\"")
parser.add_argument("--event", type=str, default=None, help = "the kind of event that you want notify")
parser.add_argument("--condition", type=str, default=None, help = "the condition expression you want to notify that moment")
parser.add_argument("--time", type=int, default=5, help = "timeout second")
parser.add_argument("--script", type=str, default=None, help = "the script to be executed after event happens")
args = parser.parse_args()

if args.event:
    event = args.event
    print ("event: %s" % (event))
if args.condition:
    expr = args.condition
    print ("condition expression: %s" % (expr))
if args.time:
    interval = args.time
    print ("timeout: %u" % (interval))
if args.script:
    shscript = args.script
    print ("script: %s" % (shscript))

def print_map():
    map_name = EVENT_LIST[event][3] + "_map"
    for k,v in b[map_name].items():
        print ("total count : %u" % (v.count))
        print ("instantaneous speed : %lf" % ((2.0 / v.inst_speed) * 1000000000))
        print ("last time : %u" % (v.last_time - v.first_time))
        try:
            print ("total size : %u" % (v.size))
        except:
            pass
#    exit()

flag = False
def call_back (pid, call_chain):
    global flag
    if flag is False:
        flag = True
        os.system(shscript)
    #for idx in call_chain:
    #    print(b.ksym(idx))

    #b.trace_print()
        print ("-------------------")
 #   print_map()

if len(sys.argv) == 1:
    print " "
    exit()

EVENT_LIST = {
        "task.create" : ["task/task_create.c", "_do_fork", "task_create_begin", "task_create"],
        "task.exec" : ["task/task_exec.c", "do_execveat_common.isra.34", "task_exec_begin", "task_exec"],
        "task.exit" : ["task/task_exit.c", "do_exit", "task_exit_begin", "task_exit"],
        "task.switch" : ["task/task_switch.c", "finish_task_switch", "task_switch_begin", "task_switch"],
        "memory.alloc" : ["memory/memory_alloc.c", "__kmalloc", "memory_alloc_begin", "memory_alloc"],
        "memory.free" : ["memory/memory_free.c", "kfree", "memory_free_begin", "memory_free"],
        "memory.alloc_page" : ["memory/memory_alloc_page.c", "__alloc_pages_nodemask", "memory_alloc_page_begin", "memory_alloc_page"],
        "memory.free_page" : ["memory/memory_free_page.c", "__free_pages_ok", "memory_free_page_begin", "memory_free_page", "free_hot_cold_page", "memory_free_page_order_zero_begin"],
        "memory.reclaim" : ["memory/memory_reclaim_bc.c", "balance_pgdat", "memory_reclaim_begin", "memory_reclaim"],
        "fs.pagecache_access" : ["fs/fs_pagecache_access.c", "pagecache_get_page", "fs_pagecache_access_begin", "fs_pagecache_access"],
        "fs.pagecache_miss" : ["fs/fs_pagecache_miss.c", "page_cache_sync_readahead", "fs_pagecache_miss_begin", "fs_pagecache_miss"],
        "fs.read_ahead" : ["fs/fs_read_ahead.c", "__do_page_cache_readahead", "fs_read_ahead_begin", "fs_read_ahead"],
        "fs.page_writeback_bg" : ["fs/fs_page_writeback_bg.c", "wb_start_background_writeback", "fs_page_writeback_bg_begin", "fs_page_writeback_bg"],
        "fs.page_writeback_per_inode" : ["fs/fs_page_writeback_per_inode.c", "__writeback_single_inode", "fs_page_writeback_per_inode_begin", "fs_page_writeback_per_inode"],
        "network.send" : ["network/network_send.c", "tcp_sendmsg", "network_send_begin", "network_send"],
        "network.recv" : ["network/network_recv.c", "tcp_recvmsg", "network_recv_begin", "network_recv"]
        }

with open(EVENT_LIST[event][0], 'r') as f:
    cfile = f.read()

rep = "EXPRESSION"
bpf_code = cfile.replace(rep, expr)

b = BPF(text = bpf_code, cb = call_back, debug=0)
for i in range(0, 10):
    b.attach_kprobe(event = EVENT_LIST[event][1], fn_name = EVENT_LIST[event][2], cpu=i)
    if event == "memory.free_page":
        b.attach_kprobe(event = EVENT_LIST[event][4], fn_name = EVENT_LIST[event][5], cpu=i)

interval = interval * 1000
b.kprobe_poll(timeout = interval)

print_map()

exit()
