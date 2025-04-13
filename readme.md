# Crawl Web Sources convert to Markdown 

Crawler to scan webistes as listed in sources.txt and snapshot as Markdown files, suitable for use in Notebook LM

When uploaded into an AI tool such as [Notebook LM from Google](https://notebooklm.google/), it allows you to run queries on this dataset, "talk" to the data, generate mindmaps and podcasts etc. 

Note if the URLs were added directly to Notebook LM, Google would not index the website contents.

![screenshot of notebook lm with using snapshot of data from selected websites](images/notebook-lm.png)

## Installation of required libs

Assuming you have Python installed.
   ```bash
   virtualenv venv
   pip install -r requirements.txt
   ```
when returning to this project
   ```bash
   source venv/bin/activate
   ```

## Configuration and Folder Structure

Settings at top of `download.py` allow configuration of download depth, number of downloads, and Markdown file structure etc. 

The following folders will be created / cleared as needed:

- `downloads_html`: Directory for storing downloaded HTML files.
- `downloads_parquet`: Directory for storing Parquet files converted from HTML.
- `downloads_md`: Directory for storing the final Markdown files. *will not be deleted*


## Usage

1. Prepare a text file containing the list of URLs to process (e.g., `sources.txt`), with one URL per line. Each URL should start with http
   ``` text
   http://www.mysample.url.com
   https://www.anotherurl.ie
   ```

2. Run the script:
   ```bash
   python3 download.py 
   ```
   - The script will look for a previous run , checking for `url_snapshot.json` (a record of previous progress)
   - If not present, the script defaults to reading `sources.txt` - it will generate the creates `url_snapshot.json` for future attempts.

   This means it's possible to run as a single run (possible memory leak in DPK crawler), or multiple times. A simple convenience script *download.sh* supports this

   Deleting the `url_snapshot.json` file will reset the list and `sources.txt` will be read again

3. The script will:
   - Download the content of the URLs.
   - Convert the content to Parquet format.
   - Generate Markdown files in the `downloads_md` directory.


4. Note about uploading to Notebook LM
   The md files can be directly imported into Notebook LM.
   It is good practice to include the url_snapshot.json (rename to .txt) so you know what information Google Gemini is using.
   MD files can be manipulated before upload as required (e.g. edited, combined)

## Robust restart functionality and Troubleshooting

1. The Crawler takes websites in blocks of X at a time (can be configured at top of `download.py`).
1. It saves a snapshot of completed websites / websites still to do in a file call `url_snapshot.json`.
1. This means if the crawl is interrupted it can be run again without missing anything / without duplication. 
1. Deleting *url_snapshot.json* resets this, the next run will start again using the urls in `sources.txt`

Since the crawler respects robots.txt, if may pause for several seconds between downloads.

In general it is safe to terminate the script, manipulate the `url_snapshot.json` file and try again



