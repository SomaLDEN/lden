/*
 * Event : task.switch
 * Data to crawl : total count, instantaneous speed, average speed
 * Used Kernel-function : finish_task_switch
 */

#include <uapi/linux/ptrace.h>

#define NUM_ARRAY_MAP_SIZE 1
#define NUM_MAP_INDEX 0
#define NUM_DELTA 10


struct circular_queue
{
    //struct circular_queue_ops *ops;
    u64 front;
    u64 back;
    //u64 element[NUM_DELTA + 1];
};

/*
struct circular_queue_ops
{
    //void (*push)(struct circular_queue *, u64);
    void (*pop)(struct circular_queue *);
    int (*full)(struct circular_queue *);
    int (*empty)(struct circular_queue *);
};

void push(struct circular_queue *queue, u64 value)
{
    if (queue->ops->full(queue))
        queue->ops->pop(queue);
    queue->element[queue->back] = value;
    queue->back = (queue->back + 1) % (NUM_DELTA + 1);
}

void pop(struct circular_queue *queue)
{
    queue->front = (queue->front + 1) % (NUM_DELTA + 1);
}

static inline int full(struct circular_queue *queue)
{
    return (queue->front == queue->back + 1 || (queue->front == 0 && queue->back == NUM_DELTA)) ? 1 : 0;
}

static inline int empty(struct circular_queue *queue)
{
    return (queue->front + 1 == queue->back || (queue->front == NUM_DELTA && queue->back == 0)) ? 1 : 0;
}
*/
struct task_switch_value
{
    u64 count;
    u64 first_time;
    u64 last_time;
    double inst_speed;
    struct circular_queue queue_info;
};

    // map where we save total count
BPF_TABLE("array", int, struct task_switch_value, task_switch_map, NUM_ARRAY_MAP_SIZE);
BPF_TABLE("array", int, u64, queue_map, NUM_DELTA + 1);

    // add task_switch_value.count one when finish_task_switch is called
int task_switch_begin(struct pt_regs *ctx)
{
    struct task_switch_value *val, val_temp;
    int queue_index, map_index = NUM_MAP_INDEX;
    u64 cnt, tim = bpf_ktime_get_ns(), *queue, queue_temp;
    val_temp.count = 0;
    val_temp.inst_speed = 0;
    val_temp.first_time = tim;
    val_temp.queue_info.front = 0;
    val_temp.queue_info.back = 1;

    val = task_switch_map.lookup_or_init(&map_index, &val_temp);
    
    ++(val->count);
    val->last_time = tim;
    
    if (val->queue_info.front == val->queue_info.back + 1 || (val->queue_info.front == 0 && val->queue_info.back == NUM_DELTA)) // when queue is full
        val->queue_info.front = (val->queue_info.front + 1) % (NUM_DELTA + 1); // pop
    
        // push
    queue_index = val->queue_info.back;
    queue = queue_map.lookup_or_init(&queue_index, &queue_temp);
    *queue = tim - val->first_time;
    val->queue_info.back = (val->queue_info.back + 1) % (NUM_DELTA + 1);

    if (val->queue_info.front == val->queue_info.back + 1 || (val->queue_info.front == 0 && val->queue_info.back == NUM_DELTA)) // when queue is full
    {
        queue_index = val->queue_info.front;
        queue = queue_map.lookup(&queue_index);
        //val->inst_speed = NUM_DELTA / (double)(tim - *queue);
    }

    cnt = val->count;
    if (EXPRESSION)
        return 1;

    return 0;
}
