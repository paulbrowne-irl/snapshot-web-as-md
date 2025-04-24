import os
import sys

# --- Configuration Constants ---
# Define your input and output parameters here
INPUT_DIR = "path/to/your/input/markdown/files"  # <<< SET YOUR INPUT DIRECTORY HERE
OUTPUT_DIR = "path/to/your/output/directory"   # <<< SET YOUR OUTPUT DIRECTORY HERE (or None to use INPUT_DIR)
MAX_SIZE_MB = 5.0  # Maximum size for each combined file in Megabytes (MB)
OUTPUT_PREFIX = "combined_output" # Prefix for the generated output filenames
SEPARATOR = "\n\n---\n\n" # Separator string between combined files

def combine_md_files():
    """
    Combines Markdown files from the INPUT_DIR into multiple output files
    in the OUTPUT_DIR, each not exceeding MAX_SIZE_MB. Uses constants
    defined at the top of the script for configuration.
    """
    # Use the global constants defined at the top
    input_dir = INPUT_DIR
    output_dir = OUTPUT_DIR
    max_size_mb = MAX_SIZE_MB
    output_prefix = OUTPUT_PREFIX
    separator = SEPARATOR

    # --- Input Validation and Setup ---
    if not input_dir or input_dir == "path/to/your/input/markdown/files":
         print("Error: Please set the INPUT_DIR constant at the top of the script.")
         sys.exit(1)

    if not os.path.isdir(input_dir):
        print(f"Error: Input directory '{input_dir}' not found or is not a directory.")
        sys.exit(1) # Exit if input directory is invalid

    if not output_dir or output_dir == "path/to/your/output/directory":
        print("Info: OUTPUT_DIR not set or is default. Using INPUT_DIR as the output directory.")
        output_dir = input_dir # Default output to input directory if not specified or default

    # Create output directory if it doesn't exist
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        print(f"Error creating output directory '{output_dir}': {e}")
        sys.exit(1)

    # Convert max size from MB to bytes
    max_size_bytes = max_size_mb * 1024 * 1024
    separator_bytes = len(separator.encode('utf-8'))

    # --- Find and Sort Markdown Files ---
    try:
        all_files = [f for f in os.listdir(input_dir) if
                     os.path.isfile(os.path.join(input_dir, f)) and f.lower().endswith('.md')]
        all_files.sort() # Sort files alphabetically for consistent order
    except OSError as e:
        print(f"Error reading input directory '{input_dir}': {e}")
        sys.exit(1)

    if not all_files:
        print(f"No .md files found in '{input_dir}'.")
        return # Exit gracefully if no markdown files are found

    print(f"Found {len(all_files)} .md files in '{input_dir}'.")
    print(f"Output directory: '{output_dir}'")
    print(f"Max file size: {max_size_mb} MB")
    print(f"Output prefix: '{output_prefix}'")

    # --- File Combination Logic ---
    output_file_index = 1
    current_output_content = ""
    current_output_size = 0
    files_in_current_output = []

    def write_output_file():
        """Helper function to write the current combined content to a file."""
        nonlocal output_file_index, current_output_content, current_output_size, files_in_current_output
        if not current_output_content:
            return # Do nothing if there's no content to write

        output_filename = f"{output_prefix}_{output_file_index}.md"
        output_filepath = os.path.join(output_dir, output_filename)
        try:
            with open(output_filepath, 'w', encoding='utf-8') as outfile:
                outfile.write(current_output_content)
            print(f"\nCreated '{output_filepath}' ({current_output_size / (1024*1024):.2f} MB) containing:")
            for fname in files_in_current_output:
                 print(f"  - {fname}")
            # Reset for the next file
            output_file_index += 1
            current_output_content = ""
            current_output_size = 0
            files_in_current_output = []
        except IOError as e:
            print(f"Error writing to output file '{output_filepath}': {e}")
            # Decide if you want to stop or continue
            # sys.exit(1) # Uncomment to stop on write error


    # --- Iterate and Combine ---
    for filename in all_files:
        input_filepath = os.path.join(input_dir, filename)
        try:
            with open(input_filepath, 'r', encoding='utf-8') as infile:
                content_to_add = infile.read()
                file_size = os.path.getsize(input_filepath) # Get actual file size

            # Calculate size needed for this file (content + separator if needed)
            size_to_add = file_size
            if current_output_size > 0: # Add separator size only if it's not the first file
                size_to_add += separator_bytes

            # --- Size Check ---
            # Special case: If a single file is larger than max_size_bytes
            if file_size > max_size_bytes and current_output_size == 0:
                 print(f"Warning: File '{filename}' ({file_size / (1024*1024):.2f} MB) is larger than the max size ({max_size_mb} MB). It will be placed in its own output file.")
                 current_output_content = content_to_add
                 current_output_size = file_size
                 files_in_current_output.append(filename)
                 write_output_file() # Write this large file immediately
                 continue # Move to the next file

            # If adding the current file exceeds the limit
            if current_output_size > 0 and (current_output_size + size_to_add) > max_size_bytes:
                write_output_file() # Write the previous combined content

            # --- Append Content ---
            # Add separator if appending to existing content
            if current_output_size > 0:
                current_output_content += separator
                current_output_size += separator_bytes

            current_output_content += content_to_add
            current_output_size += file_size
            files_in_current_output.append(filename)
            print(f". Adding '{filename}' ({file_size / (1024*1024):.2f} MB)... Current total: {current_output_size / (1024*1024):.2f} MB")


        except FileNotFoundError:
            print(f"Warning: File '{input_filepath}' not found during processing (might have been deleted). Skipping.")
        except IOError as e:
            print(f"Error reading file '{input_filepath}': {e}. Skipping.")
        except Exception as e:
            print(f"An unexpected error occurred processing file '{filename}': {e}. Skipping.")


    # --- Write the last remaining chunk ---
    write_output_file()

    print("\nMarkdown file combination process complete.")


# --- Run the main function ---
if __name__ == "__main__":
    combine_md_files()
