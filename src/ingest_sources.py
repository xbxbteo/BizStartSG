
import json
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup


# --------------------------------------------------
# 1. Define project folders and file locations
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FOLDER = PROJECT_ROOT / "data"

INVENTORY_FILE = DATA_FOLDER / "source_inventory.csv"

OUTPUT_FILE = DATA_FOLDER / "processed_sources.jsonl"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


# --------------------------------------------------
# 2. Download webpage content
# --------------------------------------------------

def download_webpage(url):
    """Download a webpage and return its HTML content."""

    headers = {
        "User-Agent": USER_AGENT
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()
    
    response.encoding = response.apparent_encoding

    return response.text


# --------------------------------------------------
# 3. Extract readable text from HTML
# --------------------------------------------------

def extract_text(html):
    """Extract the main readable text from a webpage."""

    soup = BeautifulSoup(html, "html.parser")

    # Remove elements that do not contain useful article text
    for element in soup([
        "script",
        "style",
        "nav",
        "footer",
        "header",
        "noscript",
        "svg"
    ]):
        element.decompose()

    # Prefer the main article or page content
    main_content = (
        soup.find("main")
        or soup.find("article")
        or soup.body
        or soup
    )

    title = soup.title.get_text(
        strip=True
    ) if soup.title else "Untitled document"

    text = main_content.get_text(
        separator="\n",
        strip=True
    )

    # Remove excessive blank lines
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    cleaned_text = "\n".join(lines)

    return title, cleaned_text


# --------------------------------------------------
# 4. Process all sources in the inventory
# --------------------------------------------------

def process_sources():

    print("Starting BizStart SG source ingestion...")
    print()

    # Check that the inventory exists
    if not INVENTORY_FILE.exists():
        print(f"ERROR: Cannot find {INVENTORY_FILE}")
        return

    # Read the CSV inventory
    inventory = pd.read_csv(INVENTORY_FILE)

    required_columns = [
        "source_id",
        "agency",
        "topic",
        "document_title",
        "url"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in inventory.columns
    ]

    if missing_columns:
        print(
            "ERROR: Missing columns in source inventory:",
            missing_columns
        )
        return

    successful = 0
    failed = 0

    # Create or overwrite the output file
    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as output_file:

        for _, row in inventory.iterrows():

            source_id = row["source_id"]
            agency = row["agency"]
            topic = row["topic"]
            document_title = row["document_title"]
            url = row["url"]

            print(f"Processing: {source_id}")
            print(f"URL: {url}")

            try:
                # Download the webpage
                html = download_webpage(url)

                # Extract its readable content
                page_title, page_text = extract_text(html)

                if len(page_text) < 100:
                    raise ValueError(
                        "Very little readable text was extracted."
                    )

                # Store content and source metadata together
                document = {
                    "source_id": source_id,
                    "agency": agency,
                    "topic": topic,
                    "document_title": document_title,
                    "page_title": page_title,
                    "url": url,
                    "content": page_text
                }

                output_file.write(
                    json.dumps(
                        document,
                        ensure_ascii=False
                    ) + "\n"
                )

                successful += 1

                print(
                    f"SUCCESS: Extracted "
                    f"{len(page_text)} characters."
                )

            except Exception as error:

                failed += 1

                print(
                    f"FAILED: {source_id} - {error}"
                )

            print()

            # Pause briefly between requests
            time.sleep(2)

    print("-----------------------------------")
    print("SOURCE INGESTION SUMMARY")
    print("-----------------------------------")
    print(f"Successfully processed: {successful}")
    print(f"Failed: {failed}")
    print(f"Output file: {OUTPUT_FILE}")
    print("-----------------------------------")


# --------------------------------------------------
# 5. Run the script
# --------------------------------------------------

if __name__ == "__main__":
    process_sources()
