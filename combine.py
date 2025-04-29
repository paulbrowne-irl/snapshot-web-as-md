import os
import sys
import shutil

# --- Configuration Constants ---
# Define your input and output parameters here
INPUT_DIR = "downloads_md"  # <<< SET YOUR INPUT DIRECTORY HERE
OUTPUT_DIR = "downloads_md_combine"   # <<< SET YOUR OUTPUT DIRECTORY HERE (or None to use INPUT_DIR)
MAX_SIZE_MB = 30.0  # Maximum size for each combined file in Megabytes (MB)
OUTPUT_PREFIX = "combined_output" # Prefix for the generated output filenames
SEPARATOR = "\n\n---\n\n" # Separator string between combined files

def combine_md_files():
    """
    Combines Markdown files from the INPUT_DIR into multiple output files
    in the OUTPUT_DIR, each not exceeding MAX_SIZE_MB. Uses constants
    defined at the top of the script for configuration.
    """

    # Convert max size from MB to bytes
    max_size_bytes = MAX_SIZE_MB * 1024 * 1024
    separator_bytes = len(SEPARATOR.encode('utf-8'))

    # --- Find and Sort Markdown Files ---
    try:
        all_files = [f for f in os.listdir(INPUT_DIR) if
                     os.path.isfile(os.path.join(INPUT_DIR, f)) and f.lower().endswith('.md')]
        all_files.sort() # Sort files alphabetically for consistent order
    except OSError as e:
        print(f"Error reading input directory '{INPUT_DIR}': {e}")
        sys.exit(1)

    if not all_files:
        print(f"No .md files found in '{INPUT_DIR}'.")
        return # Exit gracefully if no markdown files are found

    print(f"Found {len(all_files)} .md files in '{INPUT_DIR}'.")
    print(f"Output directory: '{OUTPUT_DIR}'")
    print(f"Max file size: {MAX_SIZE_MB} MB")
    print(f"Output prefix: '{OUTPUT_PREFIX}'")

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

        output_filename = f"{OUTPUT_PREFIX}_{output_file_index}.md"
        output_filepath = os.path.join(OUTPUT_DIR, output_filename)
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
        input_filepath = os.path.join(INPUT_DIR, filename)
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
                 print(f"Warning: File '{filename}' ({file_size / (1024*1024):.2f} MB) is larger than the max size ({MAX_SIZE_MB} MB). It will be placed in its own output file.")
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
                current_output_content += SEPARATOR
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

    # Clear update teh output dir
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    shutil.os.makedirs(OUTPUT_DIR, exist_ok=True)

    combine_md_files()
