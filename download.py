# Standard library imports
import os
import sys
import json
import shutil
import logging
import time

# Third-party imports
import nest_asyncio
import pandas as pd
from dpk_web2parquet.transform import Web2Parquet
from dpk_html2parquet.transform_python import Html2Parquet


# KEY CONFIGURATION
SINGLE_RUN_NO_LOOP = True  # Run once and exit, or loop over URLs
DEPTH = 2  # Depth of web crawling
NUM_DOWNLOADS = 200  # Maximum number of downloads per run
COMBINE_X_WEBSITES_INTO_ONE_MD_FILE = 10  # Combine multiple websites into one Markdown file

# original sources
ORIGINAL_SOURCE_FILE = "sources.txt"

# Folder paths for storing intermediate and final outputs
DOWNLOAD_HTML = "downloads_html"
DOWNLOAD_PARQUET = "downloads_parquet"
DOWNLOAD_MD = "downloads_md"

# Markdown output settings
MD_OUTPUT_FILE_BASE = "source_"

# Parquet processing settings
PQ_COLS_SKIP = ["document_id", "size"]  # Columns to skip when converting to Markdown

# Snapshot file for tracking progress
URL_SNAPSHOT_JSON = "url_snapshot.json"

# JSON STATUS_FILES
JSON_NOT_STARTED = "not started"
JSON_IN_PROGRESS = "in progress"
JSON_COMPLETE = "complete"

def read_full_dict_source_file(original_text_file:str, json_source_file: str) -> dict:
    """
    Reads URLs from a text file, iterates through each URL,
    and logs them to the console. Handles file not found errors.

    By preference it will read the json_source_file, if it exists.
    If not, it will read the original_text_file.
    
    Args:
        source_file_as_txt (str): The name of the text file containing the URLs.
        json_source_file (str): The name of the JSON file to store the URLs.        

    Returns:
        dict: A dictionary where each URL is a key, and the value is False to indicate it has not been processed.
    """
    url_dict = {}
   

    # 1. try to read the json_source_file
    try:
        with open(json_source_file, 'r') as f:
            url_dict = json.load(f)  # Load the entire JSON content
            if not isinstance(url_dict, dict):  # check if the data is a list

                logger.info(f"File '{json_source_file}' did not contain a dict. Defaulting to text file")

            else:
                logger.info(f"Valid Dict read from : {json_source_file}")
                return url_dict

    except FileNotFoundError:
        logger.error(
            f"Error: File not found - '{json_source_file}'. Defaulting to text file.")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

    
    #2. If the json_source_file does not exist, read the original_text_file
    logger.info("Attempting to read original source file {original_text_file}")   
    
    with open(original_text_file, 'r') as file:
        for line in file:
            # Remove leading/trailing whitespace, including newlines
            url = line.strip()
            # Process the URL (e.g., logger.info, check validity, etc.)
            logger.info(f"Processing URL: {url}")

            # Add a basic check that the URL starts with http or https
            if not url.startswith("http://") and not url.startswith("https://"):
                logger.info(
                    f"Warning: URL '{url}' does not start with 'http://' or 'https://'.")
            else:
                logger.info(f"Adding to dictionary: URL '{url}' with value {JSON_NOT_STARTED}")
                url_dict[url] = JSON_NOT_STARTED
        

    return url_dict

def update_json_snapshot_file(json_snapshot_file: str, url_dict: dict=None, completed_keys:list=None):
    """
    Writes a dictionary of URLs to a text file, iterating through each URL
    and logging them to the console. Handles file not found errors.

    Args:
        url_dict (dict): A dictionary where each URL is a key, and a value is False to indicate it's procession status (optional)
        completed_keys (list): A list of keys that have been processed (optional)

    """
    if url_dict is None:
        ## read from the original source file    
        loggger.info(f"Reading current snapshot from json.")  
        url_dict= read_full_dict_source_file(None,json_snapshot_file)  

    if completed_keys is not None:
        #update the url status with the "next_urls" that were processed
        logger.info(f"Updating completed keys in file")  
        
        for key in completed_keys:
            # Mark the URL as processed
            url_dict[key] = JSON_COMPLETE

    with open(json_snapshot_file, 'w') as filehandle:
            json.dump(url_dict, filehandle)
            logger.info(f"updated status to {json_snapshot_file}")


def convert_urls_to_md(json_snapshot_file:str,url_dict: dict) -> dict:
    """
    Converts a dict of URLs to markdown files.  

    Args:
        url_dict (url_dict): A list of URLs to be converted. url and true/false flag if processed
    """
    # clear interim folders
    shutil.rmtree(DOWNLOAD_PARQUET, ignore_errors=True)
    shutil.os.makedirs(DOWNLOAD_PARQUET, exist_ok=True)
    shutil.rmtree(DOWNLOAD_HTML, ignore_errors=True)
    shutil.os.makedirs(DOWNLOAD_HTML, exist_ok=True)
    # don't delete, just ensuire it exists
    shutil.os.makedirs(DOWNLOAD_MD, exist_ok=True)

    # --- 1 Download the next lot of urls ---
    counter = 0
    next_urls = []

    for key, value in url_dict.items():
        if value == JSON_NOT_STARTED:

            # add to our next list
            next_urls.append(key)

            # Mark the URL as processed
            url_dict[key] = JSON_IN_PROGRESS
            counter += 1

            logger.info(f"Processing URL: {key}")
        else:
            logger.info(f"Skipping started or completed URL: {key}")

        # Check if the number of URLs exceeds the limit
        if counter >= COMBINE_X_WEBSITES_INTO_ONE_MD_FILE:
            break

    # Snapshot the current status
    update_json_snapshot_file(json_snapshot_file,url_dict,None)

    # download these files
    logger.info(f"Starting Conversion of Web to Parquet")

    # for some reason that just outputs html files, not parquet
    Web2Parquet(urls=next_urls,
                depth=DEPTH,
                downloads=NUM_DOWNLOADS,
                folder=DOWNLOAD_HTML).transform()

    # convert html to parquet
    Html2Parquet(input_folder=DOWNLOAD_HTML,
                 output_folder=DOWNLOAD_PARQUET,
                 data_files_to_use=['.html'],
                 html2parquet_output_format="markdown"
                 ).transform()

    # Now scans a directory for .parquet files, sorts them, and converts them
    # into multiple MD files.

    logger.info(f"Scanning directory: {DOWNLOAD_PARQUET}")

    # --- 2. Find and Sort Parquet Files ---
    parquet_files = []
    try:
        for filename in os.listdir(DOWNLOAD_PARQUET):
            if filename.lower().endswith(".parquet"):
                full_path = os.path.join(DOWNLOAD_PARQUET, filename)
                parquet_files.append(full_path)
                logger.info(f"Found parquet file: {full_path}")
    except OSError as e:
        logger.error(f"Error accessing directory: {e}", file=sys.stderr)
        

    if not parquet_files:
        logger.info("No .parquet files found in the directory.")
    else:

        parquet_files.sort()
        logger.info(f"Found {len(parquet_files)} parquet files. Processing...")

        # --- 3. Process Files and Generate Markdown Files ---
        file_sources = set()
        current_md_content = ""  # Accumulate markdown content as a string

        # do the loop
        for file_path in parquet_files:  # was enumerate(parquet_files)
            logging.info(f"Processing file: {file_path}")
            filename = os.path.basename(file_path)

            # --- Read Parquet File ---
            logger.info(f"  Reading: {filename}...")

            # add first 8 letters to generate unique filename
            file_sources.add(filename[0:8])

            try:
                df = pd.read_parquet(file_path)
                # Add filename using Markdown H2
                current_md_content += f"## Data from Website: http://www.{filename[0:-8]}\n\n"

                # --- Convert DataFrame to Markdown Text ---
                if df.empty:
                    current_md_content += "_(File contains no data)_\n\n"
                else:
                    for col_name in df.columns:

                        if col_name in PQ_COLS_SKIP:
                            logging.debug(
                                f"  Skipping column '{col_name}' in file '{filename}'")

                        else:
                            # Add column name using Markdown H3
                            current_md_content += f"### {col_name}\n"

                            # Add column contents in a text code block
                            col_content_str = df[col_name].to_string(index=False)

                            current_md_content += f"```text\n{col_content_str}\n```\n\n"

            except Exception as e:
                logger.info(
                    f"  Error reading or processing parquet file '{filename}': {e}", file=sys.stderr)
                # Add error message to markdown
                current_md_content += f"**Error processing {filename}:**\n```\n{e}\n```\n\n"

            # --- Add Horizontal Rule after each file's content ---
            # This acts as a separator similar to PageBreak in PDF
            current_md_content += "---\n\n"

        # --- 4 Save the MD file if there is any data ---
        if (len(file_sources) > 0):
            output_filename = MD_OUTPUT_FILE_BASE+time.strftime("%Y%m%d-%H%M%S")+".md"


            logger.info(f"MD Output filename: {output_filename}")

            output_md_path = os.path.join(DOWNLOAD_MD, output_filename)

            if current_md_content and output_md_path:
                # Remove trailing horizontal rule if it exists before saving
                if current_md_content.endswith("\n---\n\n"):
                    # Remove last rule and newlines
                    current_md_content = current_md_content[:-5]
                try:
                    logger.info(f"Saving final Markdown: {output_md_path}...")
                    with open(output_md_path, 'w', encoding='utf-8') as f:
                        f.write(current_md_content)
                    logger.info(f"Successfully created: {output_md_path}")
                except IOError as e:
                    logger.error(
                        f"Error writing final Markdown file '{output_md_path}': {e}", file=sys.stderr)
                except Exception as e:
                    logger.error(
                        f"An unexpected error occurred while writing  file '{output_md_path}': {e}", file=sys.stderr)
        else:
            logger.error(
                f"Error: No valid sources found for file creation. Skipping file creation.")


    update_json_snapshot_file(json_snapshot_file,url_dict,next_urls)
    logger.info("\n Chunk Processing complete, status updated in json file.\n\n\n\n")


    return url_dict


if __name__ == "__main__":
    """
    Main function to get the list of sources  and call the
    iterate_urls_from_file function.
    """
    # setup logging
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)

    # Set system level parameters
    nest_asyncio.apply()
    pd.set_option("display.max_colwidth", 10000)

    # Check if any command-line arguments were provided (besides the script name itself).
    if len(sys.argv) > 1:
        # The first argument (index 1) is the value we want.
        argument_value = sys.argv[1]

        ORIGINAL_SOURCE_FILE = argument_value
        logger.info(f"Setting URL source to {ORIGINAL_SOURCE_FILE}")

        URL_SNAPSHOT_JSON = argument_value[:-4]+"_"+URL_SNAPSHOT_JSON
        logger.info(f"Setting Snapshot to {URL_SNAPSHOT_JSON}")


                    
    else:
        # If no argument was provided, print a usage message.
         logger.info(f"Defaulting URL source to {ORIGINAL_SOURCE_FILE}")
         logger.info(f"Defaulting Snapshot to {URL_SNAPSHOT_JSON}")


    # loop over the urls
    while (True):
        # Process the URLs in chunks

        # load url - Snapshot file if it exists, sources.txt if not
        url_dict = read_full_dict_source_file(ORIGINAL_SOURCE_FILE,URL_SNAPSHOT_JSON)

        if (len(url_dict) == 0):
            logger.info(f"Error: No URLs found in the file. Exiting.")
            sys.exit(1)

        logger.info(f"Processing urls - full list size {len(url_dict)} ")
        url_dict = convert_urls_to_md(URL_SNAPSHOT_JSON,url_dict)


        # break if set in config to do single run
        if (SINGLE_RUN_NO_LOOP == True):
            logger.info(f"Info: Config set not to loop . Exiting.")
            break


