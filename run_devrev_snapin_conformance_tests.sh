#!/bin/bash

NPM_INSTALL_OUTPUT_FILTER="up to date in|added [0-9]* packages, removed [0-9]* packages, and changed [0-9]* packages in|removed [0-9]* packages, and changed [0-9]* packages in|added [0-9]* packages in|removed [0-9]* packages in"

# ANSI escape code pattern to remove color codes and formatting from output
ANSI_ESCAPE_PATTERN="s/\x1b\[[0-9;]*[mK]//g"

# Maximum number of characters to display from log files
SNAP_IN_LOG_MAX_CHARS=100000
DEVREV_SERVER_LOG_MAX_CHARS=600000
PROXY_SERVER_LOG_MAX_CHARS=30000

# Function to print a log file, truncating it if it's too large
print_log_file() {
    local file_path="$1"
    local max_chars="$2"
    if [ ! -f "$file_path" ]; then
        printf "Log file not found: %s\n" "$file_path"
        return
    fi

    local total_chars=$(wc -c < "$file_path")

    if [ "$total_chars" -le "$max_chars" ]; then
        cat "$file_path"
    else
        # Truncate the file, showing 85% from the start and 15% from the end
        local start_chars=$((max_chars * 85 / 100))
        local end_chars=$((max_chars * 15 / 100))
        local omitted_chars=$((total_chars - start_chars - end_chars))

        head -c "$start_chars" "$file_path"
        printf "\n\n... [%s characters omitted] ...\n\n" "$omitted_chars"
        tail -c "$end_chars" "$file_path"
    fi
}

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the directory from where the script is being executed
EXEC_DIR="$(pwd)"
MOCK_DEVREV_SERVER_LOG="$EXEC_DIR/devrev_server.log"
PROXY_SERVER_LOG="$EXEC_DIR/proxy_server.log"

# Source environment variables from .env file - look in execution directory
if [ ! -f "$EXEC_DIR/.env" ]; then
    printf "Error: .env file not found in $EXEC_DIR. Please ensure .env file exists with required environment variables.\n"
    exit 69  # EXIT_SERVICE_UNAVAILABLE
fi

set -a  # automatically export all variables
source "$EXEC_DIR/.env"
set +a  # stop automatically exporting

# Function to check and kill any Node process running on port 8000 (React development server)
check_and_kill_processed_on_port() {
    local port=${1:-8000}  # Default to port 8000 if no port is provided
    # Find process listening on specified port
    local pid=$(lsof -i :$port -t 2>/dev/null)
    if [ ! -z "$pid" ]; then
            printf "Found server running on port $port. Killing it...\n"
            kill -9 "$pid" 2>/dev/null
    fi
}

# Function to get all child processes of a given PID and store them in a list
get_children() {
    local parent_pid=$1
    local children=$(pgrep -P $parent_pid)

    for child in $children
    do
        # Add the child process to the list
        processes_to_kill+=($child)
        # Recursively find the children of the child process
        get_children $child
    done
}

# Function to start the mock DevRev server
start_mock_devrev_server() {
    python3 -u "$SCRIPT_DIR/mock_devrev_server.py" > "$MOCK_DEVREV_SERVER_LOG" 2>&1 &
    MOCK_SERVER_PID=$!

    # Wait until the mock DevRev server prints its startup line to the log
    while true; do
        printf "Waiting for the DevRev server to start...\n"
        # If process already died, surface error and logs
        if grep -iq -E "Starting DevRev server on|Uvicorn running on" "$MOCK_DEVREV_SERVER_LOG" 2>/dev/null; then
            break
        fi
        sleep 0.1
    done

    printf "DevRev server is up and running!\n\n"
}

start_proxy_server() {
    # Check if the rate limiting proxy file exists
    if [ ! -f "$EXEC_DIR/rate_limiting_proxy.py" ]; then
        printf "Error: rate_limiting_proxy.py file not found in $EXEC_DIR/rate_limiting_proxy.py. This file should exist (and should be adopted for 3rd party service's rate limiting response format).\n"
        exit 69
    fi
    # The -u flag is critical here to disable python's output buffering, ensuring logs are written immediately.
    python3 -u "$EXEC_DIR/rate_limiting_proxy.py" > "$PROXY_SERVER_LOG" 2>&1 &
    PROXY_SERVER_PID=$!

    # Wait until the proxy server prints its startup line to the log
    while true; do
      printf "Waiting for the proxy server to start...\n"
      if grep -iq -E "Starting proxy server on" "$PROXY_SERVER_LOG" 2>/dev/null; then
        break
      fi
      sleep 0.1
    done

    if ! kill -0 "$PROXY_SERVER_PID" > /dev/null 2>&1; then
        wait "$PROXY_SERVER_PID"
        EXIT_CODE=$?
        if [ "$EXIT_CODE" -eq 69 ]; then
            echo "Proxy server failed to start. Error details:"
            cat "$PROXY_SERVER_LOG"
            exit 69
        fi
    fi

    printf "Proxy server is up and running!\n\n"
}

# Cleanup function to ensure all processes are terminated
cleanup() {
    # Kill any running npm processes started by this script
    if [ ! -z "${NPM_PID+x}" ]; then
        pkill -9 -P $NPM_PID > /dev/null 2>&1
        kill -9 $NPM_PID > /dev/null 2>&1
    fi

    # Kill React app and its children if they exist
    if [ ! -z "${SNAP_IN_PID+x}" ]; then
        local processes_to_kill=()
        get_children $SNAP_IN_PID
        
        # Kill the main process
        kill -9 $SNAP_IN_PID > /dev/null 2>&1

        # Kill all the subprocesses
        for pid in "${processes_to_kill[@]}"
        do
            kill -9 $pid > /dev/null 2>&1
        done

        if [ "${VERBOSE:-}" -eq 1 ] 2>/dev/null; then
            printf "App is terminated!\n"
        fi
    fi

    # Kill mock DevRev server if it exists
    if [ ! -z "${MOCK_SERVER_PID+x}" ]; then
        kill -9 $MOCK_SERVER_PID > /dev/null 2>&1
        if [ "${VERBOSE:-}" -eq 1 ] 2>/dev/null; then
            printf "Mock DevRev server terminated!\n"
        fi
    fi

    # Kill proxy server if it exists
    if [ ! -z "${PROXY_SERVER_PID+x}" ]; then
        kill -9 $PROXY_SERVER_PID > /dev/null 2>&1
        if [ "${VERBOSE:-}" -eq 1 ] 2>/dev/null; then
            printf "Proxy server terminated!\n"
        fi
    fi

    # Remove temporary files if they exist
    [ -f "$build_output" ] && rm "$build_output" 2>/dev/null
    [ -f "$MOCK_DEVREV_SERVER_LOG" ] && rm "$MOCK_DEVREV_SERVER_LOG" 2>/dev/null
    [ -f "$PROXY_SERVER_LOG" ] && rm "$PROXY_SERVER_LOG" 2>/dev/null
}

# Set up trap to call cleanup function on script exit, interrupt, or termination
trap cleanup EXIT SIGINT SIGTERM

# Check for and kill any existing servers from previous runs
check_and_kill_processed_on_port 8000
check_and_kill_processed_on_port 8002
check_and_kill_processed_on_port 8003
check_and_kill_processed_on_port 8004

start_mock_devrev_server

# Set HTTPS_PROXY environment variable to point to proxy server
export HTTPS_PROXY="http://localhost:8004"
start_proxy_server

# Check if chef-cli binary exists at CHEF_CLI_PATH
if [ -z "$CHEF_CLI_PATH" ] || [ ! -f "$CHEF_CLI_PATH" ] || [ ! -x "$CHEF_CLI_PATH" ]; then
    echo "Error: chef-cli not found or not executable at CHEF_CLI_PATH. Please ensure CHEF_CLI_PATH is set and points to an executable chef-cli."

    exit 69 # EXIT_SERVICE_UNAVAILABLE
fi

if [ -z "$EXTRACTED_FILES_FOLDER_PATH" ]; then
    echo "Error: extracted files folder not found at EXTRACTED_FILES_FOLDER_PATH. Please ensure EXTRACTED_FILES_FOLDER_PATH is set."
    exit 69 # EXIT_SERVICE_UNAVAILABLE
fi

# Check if EXTRACTED_FILES_FOLDER_PATH does not end with "node_$1/build"
if [[ "$EXTRACTED_FILES_FOLDER_PATH" != *"node_build/extracted_files" ]]; then
    echo "Error: EXTRACTED_FILES_FOLDER_PATH should end with 'node_$1/extracted_files'."
    echo "Note: The value of EXTRACTED_FILES_FOLDER_PATH should be <path_to_directory_where_you_rendered_the_snap-in>/node_build/extracted_files."
    exit 69 # EXIT_SERVICE_UNAVAILABLE
fi

# Check if build folder name is provided
if [ -z "$1" ]; then
  printf "Error: No build folder name provided.\n"
  printf "Usage: $0 <build_folder_name> <conformance_tests_folder>\n"
  exit 1
fi

# Check if conformance tests folder name is provided
if [ -z "$2" ]; then
  printf "Error: No conformance tests folder name provided.\n"
  printf "Usage: $0 <build_folder_name> <conformance_tests_folder>\n"
  exit 1
fi

if [[ "$3" == "-v" || "$3" == "--verbose" ]]; then
  VERBOSE=1
fi

# Ensures that if any command in the pipeline fails (like npm run build), the entire pipeline
# will return a non-zero status, allowing the if condition to properly catch failures.
set -o pipefail

# Running React application
printf "### Step 1: Starting The Snap-In in folder $1...\n"

# Define the path to the subfolder relative to execution directory
NODE_SUBFOLDER="$EXEC_DIR/node_$1"

if [ "${VERBOSE:-}" -eq 1 ] 2>/dev/null; then
  printf "Preparing Node subfolder: $NODE_SUBFOLDER\n"
fi

# Check if the node subfolder exists
if [ -d "$NODE_SUBFOLDER" ]; then
  # Find and delete all files and folders except "node_modules"
  find "$NODE_SUBFOLDER" -mindepth 1 ! -path "$NODE_SUBFOLDER/node_modules*" -exec rm -rf {} +
  
  if [ "${VERBOSE:-}" -eq 1 ] 2>/dev/null; then
    printf "Cleanup completed, keeping 'node_modules'.\n"
  fi
else
  if [ "${VERBOSE:-}" -eq 1 ] 2>/dev/null; then
    printf "Subfolder does not exist. Creating it...\n"
  fi

  mkdir -p "$NODE_SUBFOLDER"
fi

# Use absolute paths for source directory
cp -R "$EXEC_DIR/$1"/* "$NODE_SUBFOLDER"

# Move to the subfolder
cd "$NODE_SUBFOLDER" 2>/dev/null

if [ $? -ne 0 ]; then
  printf "Error: Node build folder '$NODE_SUBFOLDER' does not exist.\n"
  exit 2
fi

npm install --prefer-offline --no-audit --no-fund --loglevel error | grep -Ev "$NPM_INSTALL_OUTPUT_FILTER"

if [ $? -ne 0 ]; then
  printf "Error: Installing Node modules.\n"
  exit 2
fi

if [ "${VERBOSE:-}" -eq 1 ] 2>/dev/null; then
  printf "Building the application...\n"
fi

build_output=$(mktemp)

npm run build --loglevel silent > "$build_output" 2>&1

if [ $? -ne 0 ]; then
  printf "Error: Building application.\n"
  cat "$build_output"
  rm "$build_output"
  exit 2
fi

rm "$build_output"

if [ "${VERBOSE:-}" -eq 1 ] 2>/dev/null; then
  printf "Starting the application...\n"
fi

# Start the snap-in in the background and redirect output to a log file
npm run test:server -- local > app.log 2>&1 &

# Capture the process ID of the npm start command
SNAP_IN_PID=$!
NPM_PID=$(pgrep -P $SNAP_IN_PID npm)

# Wait for the "compiled successfully!" message in the log file
while true; do
  printf "Waiting for The Snap-In to start...\n"
  if grep -iq -E "Server is running at" app.log; then
    break
  fi
  sleep 0.1
done

printf "The Snap-In is up and running!\n\n"

# Execute all conformance tests in the build folder
printf "### Step 2: Running conformance tests $2...\n"

# Move back to the execution directory
cd "$EXEC_DIR"

# Define the path to the conformance tests subfolder
NODE_CONFORMANCE_TESTS_SUBFOLDER="$EXEC_DIR/node_$2"

if [ "${VERBOSE:-}" -eq 1 ] 2>/dev/null; then
  printf "Preparing conformance tests Node subfolder: $NODE_CONFORMANCE_TESTS_SUBFOLDER\n"
fi

# Check if the conformance tests node subfolder exists
if [ -d "$NODE_CONFORMANCE_TESTS_SUBFOLDER" ]; then
  # Find and delete all files and folders except "node_modules"
  find "$NODE_CONFORMANCE_TESTS_SUBFOLDER" -mindepth 1 ! -path "$NODE_CONFORMANCE_TESTS_SUBFOLDER/node_modules*" -exec rm -rf {} +
  
  if [ "${VERBOSE:-}" -eq 1 ] 2>/dev/null; then
    printf "Cleanup completed, keeping 'node_modules'.\n"
  fi
else
  if [ "${VERBOSE:-}" -eq 1 ] 2>/dev/null; then
    printf "Subfolder does not exist. Creating it...\n"
  fi

  mkdir -p "$NODE_CONFORMANCE_TESTS_SUBFOLDER"
fi

# Use absolute paths for source directory
cp -R "$EXEC_DIR/$2"/* "$NODE_CONFORMANCE_TESTS_SUBFOLDER"

# Move to the subfolder with tests
cd "$NODE_CONFORMANCE_TESTS_SUBFOLDER" 2>/dev/null

if [ $? -ne 0 ]; then
  printf "Error: conformance tests Node folder '$NODE_CONFORMANCE_TESTS_SUBFOLDER' does not exist.\n"
  exit 2
fi

npm install --prefer-offline --no-audit --no-fund --loglevel error | grep -Ev "$NPM_INSTALL_OUTPUT_FILTER"

if [ $? -ne 0 ]; then
  printf "Error: Installing Node modules for conformance tests failed.\n"
  exit 2
fi

printf "\n#### Running conformance tests...\n"

npm test -- --runInBand --setupFilesAfterEnv="$SCRIPT_DIR/jest.setup.js" --detectOpenHandles --forceExit 2>&1 | sed -E "$ANSI_ESCAPE_PATTERN"
conformance_tests_result=$?

printf "\n#### Output of the DevRev server log file:\n\n"
print_log_file "$MOCK_DEVREV_SERVER_LOG" "$DEVREV_SERVER_LOG_MAX_CHARS"
printf "\n#### Output of The Snap-In log file:\n"
print_log_file "$NODE_SUBFOLDER/app.log" "$SNAP_IN_LOG_MAX_CHARS"
# uncomment if you need the logs of the proxy server
# printf "\n#### Output of the proxy server log file:\n\n"
# print_log_file "$PROXY_SERVER_LOG" "$PROXY_SERVER_LOG_MAX_CHARS"
printf "\n"

if [ $conformance_tests_result -ne 0 ]; then
  if [ "${VERBOSE:-}" -eq 1 ] 2>/dev/null; then
    printf "Error: Conformance tests have failed.\n"
  fi
  exit 2
fi