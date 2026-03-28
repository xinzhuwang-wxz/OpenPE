#!/usr/bin/env agfs

# Enqueue Task Script
#
# Usage:
#   ./enqueue_task.as <task_data> [queue_path]
#
# Arguments:
#   task_data   - Task content (required)
#   queue_path  - Queue path (default: /queue/mem/task_queue)
#
# Examples:
#   ./enqueue_task.as "process file.txt"
#   ./enqueue_task.as "send email" /queue/mem/email_queue

# Check arguments
if [ -z "$1" ]; then
    echo "Usage: $0 <task_data> [queue_path]"
    echo ""
    echo "Examples:"
    echo "  $0 \"process file.txt\""
    echo "  $0 \"run backup\" /queue/mem/backup_queue"
    exit 1
fi

TASK_DATA=$1

# Queue path
if [ -n "$2" ]; then
    QUEUE_PATH=$2
else
    QUEUE_PATH=/queue/mem/task_queue
fi

ENQUEUE_FILE=$QUEUE_PATH/enqueue
SIZE_FILE=$QUEUE_PATH/size

# Ensure queue exists
mkdir $QUEUE_PATH

# Enqueue
echo "$TASK_DATA" > $ENQUEUE_FILE

echo "Task enqueued successfully!"
echo "  Queue: $QUEUE_PATH"
echo "  Data:  $TASK_DATA"

# Show current queue size
size=$(cat $SIZE_FILE)
echo "  Queue size: $size"
