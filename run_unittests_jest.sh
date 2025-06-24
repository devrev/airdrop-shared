#!/bin/bash

# ANSI escape code pattern to remove color codes and formatting from output
ANSI_ESCAPE_PATTERN="s/\x1b\[[0-9;]*[mK]//g"

# Ensures that if any command in the pipeline fails (like npm run build), the entire pipeline
# will return a non-zero status, allowing the if condition to properly catch failures.
set -o pipefail

# Get the absolute path of the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if subfolder name is provided
if [ -z "$1" ]; then
  echo "Error: No subfolder name provided."
  echo "Usage: $0 <subfolder_name>"
  exit 1
fi

# Extract just the folder name from the path
FOLDER_NAME=$(basename "$1")
NODE_SUBFOLDER="node_${FOLDER_NAME}"

if [ "${VERBOSE:-}" -eq 1 ] 2>/dev/null; then
  printf "Preparing Node subfolder: $NODE_SUBFOLDER\n"
fi

printf "### Step 1: Preparing Node subfolder $NODE_SUBFOLDER and building the application...\n"

# Check if the node subfolder exists
if [ -d "$NODE_SUBFOLDER" ]; then
  # Find and delete all files and folders except "node_modules", "build", and "package-lock.json"
  find "$NODE_SUBFOLDER" -mindepth 1 ! -path "$NODE_SUBFOLDER/node_modules*" ! -path "$NODE_SUBFOLDER/build*" ! -name "package-lock.json" -exec rm -rf {} +
  
  if [ "${VERBOSE:-}" -eq 1 ] 2>/dev/null; then
    printf "Cleanup completed, keeping 'node_modules' and 'package-lock.json'.\n"
  fi
else
  if [ "${VERBOSE:-}" -eq 1 ] 2>/dev/null; then
    printf "Subfolder does not exist. Creating it...\n"
  fi

  mkdir $NODE_SUBFOLDER
fi

cp -R "$1"/* "$NODE_SUBFOLDER"

# Move to the subfolder
cd "$NODE_SUBFOLDER" 2>/dev/null

if [ $? -ne 0 ]; then
  echo "Error: Subfolder '$1' does not exist."
  exit 2
fi

# Install libraries
npm install --silent

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

printf "### Step 2: Running unittests in $FOLDER_NAME...\n"

npm test -- --runInBand --silent --setupFilesAfterEnv="$SCRIPT_DIR/jest.setup.js" --detectOpenHandles 2>&1 | sed -E "$ANSI_ESCAPE_PATTERN"
TEST_EXIT_CODE=$?

# Check if tests failed
if [ $TEST_EXIT_CODE -ne 0 ]; then
  echo "Error: Tests failed with exit code $TEST_EXIT_CODE"
  exit $TEST_EXIT_CODE
fi