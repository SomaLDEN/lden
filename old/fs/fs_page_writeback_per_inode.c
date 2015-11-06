/*
 * Event : fs.page_writeback_per_inode
 * Data to crawl : total count, total size
 * Used Kernel-function : __writeback_single_inode
 */

#include <uapi/linux/ptrace.h>
#include <linux/writeback.h>

#define NUM_ARRAY_MAP_SIZE 1
#define NUM_MAP_INDEX 0

struct fs_page_writeback_per_inode_value
{
    u64 count;
    u64 size;
};

BPF_TABLE("array", int, struct fs_page_writeback_per_inode_value, fs_page_writeback_per_inode_map, NUM_ARRAY_MAP_SIZE);

int fs_page_writeback_per_inode_begin(struct pt_regs *ctx, struct inode *inode, struct writeback_control *wbc){
    struct fs_page_writeback_per_inode_value *val, val_temp;
    int map_index = NUM_MAP_INDEX;
    u64 cnt, siz;
    val_temp.count = 0;
    val_temp.size = 0;

    val = fs_page_writeback_per_inode_map.lookup_or_init(&map_index, &val_temp);
    ++(val->count);
    val->size += wbc->nr_to_write; //maybe size

    cnt = val->count;
    siz = val->size;
    if(EXPRESSION)
        return 1;

    return 0;
}