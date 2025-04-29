#!/bin/bash

# Script to execute a Download script a specified number of times.
# Usage: ./repeat_download.sh <url_source_file> <loop_count> 

# --- Argument Validation ---

# Check if exactly two arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <url_source_file> <loop_count> "
    echo "Example: $0 sources_1.txt 5 "
    exit 1 # Exit with an error code
fi

# Assign arguments to variables for clarity
SOURCE_FILE_NAME=$1
LOOP_COUNT=$2

# Check if the first argument (SOURCE_FILE_NAME_name) is an existing file
if [ ! -f "$SOURCE_FILE_NAME" ]; then
    echo "Error: List of URL sources '$SOURCE_FILE_NAME' not found."
    exit 1 # Exit with an error code
fi

# Check if the second argument (loop_count) is a positive integer
if ! [[ "$LOOP_COUNT" =~ ^[1-9][0-9]*$ ]]; then
    echo "Error: <loop_count> must be a positive integer."
    echo "Usage: $0 <loop_count> <SOURCE_FILE_NAME_name>"
    exit 1 # Exit with an error code
fi

# --- Virtual Environment Check ---

# Check if a virtual environment is already active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "No active Python virtual environment detected."
    # Attempt to activate a common virtual environment (venv or .venv)
    # Assumes the venv is in the current directory where the script is run
    VENV_PATH=""
    if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
        VENV_PATH="venv/bin/activate"
    elif [ -d ".venv" ] && [ -f ".venv/bin/activate" ]; then
        VENV_PATH=".venv/bin/activate"
    fi

    if [ -n "$VENV_PATH" ]; then
        echo "Attempting to activate virtual environment: $VENV_PATH"
        # Source the activate script to load the venv into the current shell
        source "$VENV_PATH"
        if [ $? -ne 0 ]; then
            echo "Error: Failed to activate virtual environment at $VENV_PATH."
            # Decide if you want to exit or continue with the system python
            # exit 1 # Uncomment to exit if activation fails
        else
             echo "Virtual environment activated."
        fi
    else
        echo "Warning: Could not find a 'venv/bin/activate' or '.venv/bin/activate' script in the current directory."
        echo "Continuing with system Python interpreter."
        # Decide if you want to exit if no venv is found
        # exit 1 # Uncomment to require a venv
    fi
else
    echo "Active virtual environment detected: $VIRTUAL_ENV"
fi


# --- Main Loop ---

echo "Starting execution loop..."
echo "Will run python3 download.sh '$SOURCE_FILE_NAME' $LOOP_COUNT times."

# Loop from 1 to LOOP_COUNT
for (( i=1; i<=LOOP_COUNT; i++ ))
do
   echo "--- Iteration $i of $LOOP_COUNT ---"
   # Execute the Python script using the python3 interpreter
   python3 download.py "$SOURCE_FILE_NAME"

done

echo "--- Loop finished ---"

exit 0 # Exit successfully
