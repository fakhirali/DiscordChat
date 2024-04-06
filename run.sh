#!/bin/bash

# Function to clean up processes
cleanup() {
    echo "Terminating processes..."
    # Terminate all child processes
    pkill -P $$
    exit 0
}

# Trap Ctrl-C signal
trap 'cleanup' INT

# Start the first process


python3 llm_server.py &

python3 main.py &

python3 epicac.py

# Wait for any process to exit
#wait -n

# Wait for all the processes to exit
wait

# Exit with status of process that exited first
exit $?