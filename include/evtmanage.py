# coding=utf-8


class EventManager:
    """
    LDEN에서 다루는 이벤트들을 관리하는 클래스이다.
    기본적으로 general.c 코드를 선택된 이벤트에 맞게 변환한 뒤 필요한 데이터를 리턴하는 작업을 한다.
    """

    def __init__(self):
        self.source = self.read_file("../src/general.c")
        self.EVENT_LIST = {
            "task.create": self.task_create(),
            "task.exec": self.task_exec(),
            "task.exit": self.task_exit(),
            "task.switch": self.task_switch(),
            "memory.alloc": self.memory_alloc(),
            "memory.free": self.memory_free(),
            "memory.alloc_page": self.memory_alloc_page(),
            # "memory.free_page": ["memory/memory_free_page.c", "__free_pages_ok", "memory_free_page_begin", "memory_free_page", "free_hot_cold_page", "memory_free_page_order_zero_begin"],
            "memory.reclaim": self.memroy_reclaim(),
            "fs.pagecache_access": self.fs_pagecache_access(),
            "fs.pagecache_miss": self.fs_pagecache_miss(),
            "fs.read_ahead": self.fs_read_ahead(),
            # "fs.page_writeback_bg": self.fs_page_writeback_bg(),
            "fs.page_writeback_per_inode": self.fs_page_writeback_per_inode(),
            "network.tcp_send": self.network_tcp_send(),
            "network.tcp_recv": self.network_tcp_recv(),
            "network.udp_send": self.network_udp_send(),
            "network.udp_recv": self.network_udp_recv(),
        }

    def read_file(self, path):
        with open(path, 'r') as f:
            return f.read()

    def task_create(self):
        return self.source\
                   .replace("HEADER", '')\
                   .replace("PARAMETER", '')\
                   .replace("SIZE", '0'),\
               "do_fork"

    def task_exec(self):
        return self.source\
                   .replace("HEADER", '')\
                   .replace("PARAMETER", '')\
                   .replace("SIZE", '0'),\
               "sys_execve"

    def task_exit(self):
        return self.source\
                   .replace("HEADER", '')\
                   .replace("PARAMETER", '')\
                   .replace("SIZE", '0'),\
               "do_exit"

    def task_switch(self):
        return self.source\
                   .replace("HEADER", '')\
                   .replace("PARAMETER", '')\
                   .replace("SIZE", '0'),\
               "finish_task_switch"

    def memory_alloc(self):
        return self.source\
                   .replace("HEADER", '')\
                   .replace("PARAMETER", ', size_t size')\
                   .replace("SIZE", '(u64)size'),\
               "__kmalloc"

    def memory_free(self):
        return self.source\
                   .replace("HEADER", '')\
                   .replace("PARAMETER", '')\
                   .replace("SIZE", '0'),\
               "kfree"

    def memory_alloc_page(self):
        return self.source\
                   .replace("HEADER", '#include<asm/page.h>')\
                   .replace("PARAMETER", ', gfp_t gfp_mask, unsigned int order')\
                   .replace("SIZE", '(1<<(u64)order)*PAGE_SIZE'),\
               "__alloc_pages_nodemask"

    def memory_free_page(self):
        return self.source\
                   .replace("HEADER", '#include <linux/pagevec.h>\n#include<asm/page.h>')\
                   .replace("PARAMETER", ', struct page *page, unsinged int order')\
                   .replace("SIZE", '(1 << (u64)order) * PAGE_SIZE'),\
               "__free_pages_ok"

    def memroy_reclaim(self):
        return self.source\
                   .replace("HEADER", '#include <linux/mmzone.h>\n#include<asm/page.h>')\
                   .replace("PARAMETER", ', struct zonelist *zonelist, int order, gfp_t gfp_mask')\
                   .replace("SIZE", '(1<<order) * PAGE_SIZE'),\
               "try_to_free_pages"

    def fs_pagecache_access(self):
        return self.source\
                   .replace("HEADER", '')\
                   .replace("PARAMETER", '')\
                   .replace("SIZE", '0'),\
               "pagecache_get_page"

    def fs_pagecache_miss(self):
        return self.source\
                   .replace("HEADER", '')\
                   .replace("PARAMETER", '')\
                   .replace("SIZE", '0'),\
               "page_cache_sync_readahead"

    def fs_read_ahead(self):
        return self.source\
                   .replace("HEADER", "#include <linux/mm_types.h>\n#include<asm/page.h>")\
                   .replace("PARAMETER", '')\
                   .replace("SIZE", '(ctx->r8) * PAGE_SIZE'),\
               "__do_page_cache_readahead"

    def fs_page_writeback_bg(self):
        return self.source\
                   .replace("HEADER", "#include <linux/backing-dev-defs.h>")\
                   .replace("PARAMETER", ',struct bdi_writeback * wb')\
                   .replace("SIZE", '0'),\
               "wb_start_background_writeback"

    def fs_page_writeback_per_inode(self):
        return self.source\
                   .replace("HEADER", "#include <linux/writeback.h>")\
                   .replace("PARAMETER", ',struct inode *inode, struct writeback_control *wbc')\
                   .replace("SIZE", 'wbc->nr_to_write'),\
               "wb_start_background_writeback"

    def network_tcp_recv(self):
        return self.source\
                   .replace("HEADER", "#include <net/tcp.h>")\
                   .replace("PARAMETER", ',struct sock *sk, struct msghdr *msg, size_t len')\
                   .replace("SIZE", '(u64)len'),\
               "tcp_recvmsg"

    def network_tcp_send(self):
        return self.source\
                   .replace("HEADER", "#include <net/tcp.h>\n #include <net/inet_common.h>")\
                   .replace("PARAMETER", ',struct sock *sk, struct msghdr *msg, size_t size')\
                   .replace("SIZE", '(u64)size'),\
               "tcp_sendmsg"

    def network_udp_send(self):
        return self.source\
                   .replace("HEADER", "#include <net/udp.h>")\
                   .replace("PARAMETER", ',struct sock *sk, struct msghdr *msg, size_t len')\
                   .replace("SIZE", '(u64)len'),\
               "udp_sendmsg"

    def network_udp_recv(self):
        return self.source\
                   .replace("HEADER", "#include <net/udp.h>")\
                   .replace("PARAMETER", ',struct sock *sk, struct msghdr *msg, size_t len')\
                   .replace("SIZE", '(u64)len'),\
               "udp_recvmsg"
