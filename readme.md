# Review web sources and snapshot as Markdown 

Crawler to scan websites as listed in sources.txt and snapshot as Markdown files, suitable for use in Notebook LM

When uploaded into an AI tool such as [Notebook LM from Google](https://notebooklm.google/), it allows you to run queries on this dataset, "talk" to the data, generate mindmaps and podcasts etc. 

Why is this needed? If the URLs are added directly to Notebook LM, Google does not index the website contents.

![screenshot of notebook lm with using snapshot of data from selected websites](images/notebook-lm.png)

## Installation of required libs

Assuming you have Python installed.
   ```bash
   virtualenv venv
   pip install -r requirements.txt
   ```
When returning to this project
   ```bash
   source venv/bin/activate
   ```

## Configuration and Folder Structure

Settings at top of `download.py` allow configuration of download depth, number of downloads, and Markdown file structure etc. 

The following folders will be created / cleared as needed:

- `downloads_html`: Directory for storing downloaded HTML files.
- `downloads_parquet`: Directory for storing Parquet files converted from HTML.
- `downloads_md`: Directory for storing the final Markdown files. *will not be deleted only created*


## Usage

1. Prepare a text file containing the list of URLs to process (e.g. `sources.txt`), with one URL per line. Each URL should start with http or https.
   ``` text
   http://www.mysampleurl.com
   https://www.anotherurl.ie
   ```

2. Run the script:
   ```bash
   python3 download.py 
   ```
   The script will look for a previous run , checking for `url_snapshot.json` (a record of previous progress)
   If not present, the script defaults to reading `sources.txt` - it will generate `url_snapshot.json` for future attempts.

   Deleting the `url_snapshot.json` file will reset the list and `sources.txt` will be read again

   Noting it is possible to provide a different source file name e.g. 
   ```bash
   python3 download.py different_source.txt
   ```
   In this case, the json snapthot will be different_source_url_snapshot.json. This supports running the script in paralell, with different sources (as web crawling and spidering can take a significant amount of time)


3. The script will:
   - Download the content of the URLs/ websites (including following internal links to a depth specified in the config).
   - Convert the content to Parquet format.
   - Generate the Markdown files with this content in the `downloads_md` directory.

4. Note about uploading to NotebookLM
   The md files generated can be directly imported into Notebook LM.
   It is good practice to include the url_snapshot.json (rename to .txt) so you know what information Google Gemini is using.
   MD files can be manipulated before upload as required (e.g. edited, combined).

## Usage - Multiple download script
A shell script is provided for convenience. It avoids any possibility of a memory leak, and works best when ```NO_LOOP``` in ```download.py``` is set to ```true```.

This script.
1. Sets the Python virtual environment if not already setup
1. takes the source file
1. loops for x time, calling the Python ```download.py``` as a new process each time.

```bash
   ./repeat_download.sh <url_source_file> <loop_count> 
```
For example
```bash
   ./repeat_download.sh sources_1.txt 10 
```

## Robust restart functionality and troubleshooting

The script only reads information, so nothing can "break". Any information in the download folders can be safely deleted (as the info will be recreated during a future script run).

1. The Crawler takes websites in blocks of X at a time (can be configured at top of `download.py`).
1. It saves a snapshot of completed websites / websites remaining in `url_snapshot.json`.
1. This means if the crawl is interrupted it can be run again without missing anything but also without duplication. 
1. Deleting `url_snapshot.json` resets this, the next run will start again using the urls in `sources.txt`

Since the crawler respects robots.txt, it may pause for several seconds between downloads.

In general it is safe to terminate the script, manipulate the `url_snapshot.json` file and try again.

The flag `SINGLE_RUN_NO_LOOP` in `download.py` in the script sets the script to run once (one block of urls), or multiple times until all urls have been captured. This allows for a workaround (possible memory leak in the DPK / Scrapy crawler used). A simple convenience script `read-download.sh` supports this i.e. Python is allowed to exit, memory freed up, then script called again for the next run.

The script (and Python program) are almost thread-safe - it is ok to have multiple terminal windows open and run them concurrently. The various scripts will read / write their status to the Snapshot file in a way that singals their progress (i.e. will take the next block of urls not already started, will add their url status update based on the latest version of the file.)

To enable this - the script takes an (optional) Parameter of the sources e.g. sources1.txt, sources2.txt etc . This gives an even more robust paralell option, since ti will snaphot progress as sources1_url_snapshot.json etc, meaning there is no risk of it getting overwritten



