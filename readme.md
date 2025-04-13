# Crawl Web Sources convert to Markdown 

Crawler to download list from sources.txt and output as md , suitable for use in Notebook LM

This sub-folder contains a tool for crawling web sources, converting their content into Parquet files, and generating Markdown files for further analysis. It is designed to process a list of URLs, download their content, and transform the data into a structured Markdown format.

When uploaded into an AI tool such as [Notebook LM from Google](https://notebooklm.google/), it allows you to run queries on this dataset, "talk" to the data, generate mindmaps and podcasts etc. Note the URLs were added directly to Notebook LM, it Google would not index the website contents.

![screenshot of notebook lm with using snapt of data from selected websites](images/notebook-lm.png)

## Configuration

- *download.py*: Allows configuration of download depth, number of downloads, and Markdown file structure.

## Folder Structure - will be deleted / created as needed

- `downloads_html`: Directory for storing downloaded HTML files.
- `downloads_parquet`: Directory for storing Parquet files converted from HTML.
- `downloads_md`: Directory for storing the final Markdown files. *will not be deleted*

## Installation of required libs

   ```bash
   virtualenv venv
   pip install -r requirements.txt
   ```
when returning to this
   ```bash
   source venv/bin/activate
   ```


3. Ensure the following directories exist or will be created during runtime:
   - `downloads_html`
   - `downloads_parquet`
   - `downloads_md`

## Usage

1. Prepare a text file containing the list of URLs to process (e.g., `sources.txt`), with one URL per line.

2. Run the script:
   ```bash
   python3 download.py 
   ```
   - The script will look for a url_snapshot.json (a record)
   - The script defaults to `sources.txt` and creates url_snapshot.json as needed to record progress

   This means it's possible to run as a single one (possible memory leak in DPK crawler), mulitple times
   with download.sh being a simple script file to support this

   Deleting the url_snapshot.json file will reset the list

3. The script will:
   - Download the content of the URLs.
   - Convert the content to Parquet format.
   - Generate Markdown files in the `downloads_md` directory.

4. ### Note about uploading to Notebook LM

