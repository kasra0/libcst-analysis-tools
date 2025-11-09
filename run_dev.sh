#!/bin/bash

# Export function so subshells can use it
function run_script {
    # Kill any existing Python processes running the same script
    pkill -9 -f "python.*$(basename $1)" 2>/dev/null
    sleep 0.1
    
    # Clear screen and reset cursor
    printf "\033c"
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔄 Restarted at $(date '+%H:%M:%S')"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Run Python with proper signal handling
    trap 'printf "\033c"; exit' INT TERM
    python "$@"
    
    # Restore normal terminal state
    stty sane 2>/dev/null
}
export -f run_script

#ensure watchdog is installed
source env-libcst/bin/activate
if ! python -c "import watchdog" &> /dev/null; then
    echo "watchdog not found, install it first with: pip install watchdog"
fi


function watch_and_run {
    watchmedo shell-command \
        --patterns='**/*.py;**/*.txt' \
        --recursive \
        --command="bash -c \"run_script $1\"" 
}
echo "Starting development environment..."
#sleep for 2 seconds to give user time to read the message
sleep 2
clear
# use arguments passed to run_dev.sh or default to demo_inspect_members.py
watch_and_run "${1:-./demo_inspect_members.py}"