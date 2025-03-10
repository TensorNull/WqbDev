#!/bin/bash

# Define log files and Python script names
LOG_FILE="simulation.log"  # Log file to monitor
PYTHON_SCRIPT="simulator.py"  # Python script to run
MONITOR_LOG="monitor.log"  # Log file for the monitor script

# Timeout threshold (in seconds) - if the log file hasn't been updated for this duration, restart the script
LOG_TIMEOUT=600

# Clear the monitor log file
> "$MONITOR_LOG"

# Log function that outputs to both terminal and log file
log_message() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp=$(date +"%Y-%m-%d %H:%M:%S")  # Standardized timestamp format
    echo "$timestamp - $level - $message" | tee -a "$MONITOR_LOG"
}

log_message "INFO" "Monitor script started. Log timeout set to $LOG_TIMEOUT seconds."

# Enter infinite loop, periodically checking the log file's update time
while true; do
    # Record current check time
    log_message "INFO" "Checking log file status..."

    # If log file doesn't exist, restart the Python script
    if [ ! -f "$LOG_FILE" ]; then
        log_message "WARNING" "Log file is missing. Restarting script..."
        nohup python3 "$PYTHON_SCRIPT" > /dev/null 2>&1 &
        NEW_PID=$!  # Get the PID of the newly started Python process
        log_message "INFO" "$PYTHON_SCRIPT script started with PID: $NEW_PID"
        sleep 5  # Wait for script to initialize
        continue  # Skip the rest of this iteration and start the next loop
    fi

    # Get the last modification time of the log file (timestamp in seconds)
    LAST_MODIFIED=$(stat -c %Y "$LOG_FILE")
    # Get current time (timestamp in seconds)
    CURRENT_TIME=$(date +%s)
    # Calculate time difference between current time and last log modification
    TIME_DIFF=$((CURRENT_TIME - LAST_MODIFIED))

    log_message "INFO" "Log last modified $TIME_DIFF seconds ago."

    # If log file hasn't been updated for longer than LOG_TIMEOUT, assume the script is hung and needs restart
    if [ "$TIME_DIFF" -gt "$LOG_TIMEOUT" ]; then
        log_message "ERROR" "Log file stale for more than $LOG_TIMEOUT seconds. Restarting script..."

        # Find the process ID of the running Python script
        PYTHON_PID=$(pgrep -f "$PYTHON_SCRIPT")

        # If process is found, terminate it
        if [ -n "$PYTHON_PID" ]; then
            log_message "INFO" "Sending SIGINT to process $PYTHON_PID"
            kill -SIGINT "$PYTHON_PID"  # Send SIGINT signal for graceful termination

            TIMEOUT=300  # Maximum wait time of 5 minutes (300 seconds)
            ELAPSED=0

            while ps -p "$PYTHON_PID" > /dev/null; do
                if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
                    log_message "CRITICAL" "Process did not exit after 5 minutes. Forcibly killing it..."
                    kill -9 "$PYTHON_PID"  # Force kill the process
                    break
                fi
                sleep 10  # Check process status every 10 seconds
                ELAPSED=$((ELAPSED + 10))
            done
        fi

        sleep 5  # Brief wait to ensure resources are released
        # Restart the Python script, redirecting output to /dev/null to avoid interference
        nohup python3 "$PYTHON_SCRIPT" > /dev/null 2>&1 &
        NEW_PID=$!  # Get PID of newly started Python process
        log_message "INFO" "$PYTHON_SCRIPT restarted with PID: $NEW_PID"
    fi

    sleep 300
done
