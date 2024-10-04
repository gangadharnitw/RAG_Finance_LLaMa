import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import re
import json

# SEC EDGAR requires a User-Agent header with your contact information
HEADERS = {
    "User-Agent": "Gangadhar (gangs_abcd@gmail.com)"
}
BASE_DIR = "downloads"


# Function to get the CIK using the SEC's full-text search API
def get_cik(ticker):
    api_url = f"https://www.sec.gov/files/company_tickers.json"

    response = requests.get(api_url, headers=HEADERS)

    if response.status_code != 200:
        print(f"Failed to fetch company tickers. HTTP status code: {response.status_code}")
        return None

    # Search for the CIK by ticker
    data = response.json()

    for entry in data.values():
        if entry["ticker"] == ticker.upper():
            cik = str(entry["cik_str"]).zfill(10)  # CIKs are typically padded to 10 digits
            return cik

    print(f"CIK not found for ticker: {ticker}")
    return None


# Function to get the latest financial filing links and their dates for a given CIK (e.g., 10-K or 10-Q)
def get_financial_report_links(cik, report_type="10-K", count=5):
    base_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type={report_type}&count={100}&output=atom"
    response = requests.get(base_url, headers=HEADERS)
    print(base_url)

    if response.status_code != 200:
        print(f"Failed to fetch filings for CIK: {cik}. HTTP status code: {response.status_code}")
        return []

    # Use the XML parser for the response content
    soup = BeautifulSoup(response.content, "xml")

    # Find the filing links and their corresponding filing dates
    filings = []
    entries = soup.find_all("entry")
    if not entries:
        print(f"No {report_type} filings found for CIK: {cik}")
        return []

    for entry in entries:
        filing_href = entry.find("link", {"rel": "alternate"})
        filing_date = entry.find("updated")  # "updated" contains the filing date in ISO format with timezone

        if filing_href and filing_date:
            filing_url = filing_href['href']
            filing_date_str = filing_date.text.strip()

            # Parse the date into a datetime object, accounting for timezone offset
            filing_date_obj = datetime.strptime(filing_date_str, "%Y-%m-%dT%H:%M:%S%z")

            # Append the filing URL and the filing date
            filings.append((filing_url, filing_date_obj))

    # Sort filings by date (most recent first)
    filings_sorted = sorted(filings, key=lambda x: x[1], reverse=True)

    # Return only the specified number of filings
    return filings_sorted[:count]


# Function to download the primary financial report (HTML or XBRL content)
def download_primary_report(filing_index_url, filing_date, download_dir):
    # Get the filing index page
    response = requests.get(filing_index_url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch filing page from: {filing_index_url}. HTTP status code: {response.status_code}")
        return

    # Parse the page as HTML (since it's an index page)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the table with the document links
    table = soup.find("table", class_="tableFile")
    if table is None:
        print(f"Could not find the table with documents on page: {filing_index_url}")
        return

    rows = table.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        if len(cols) > 3 and ('Complete submission text' in cols[1].text):
            doc_href = cols[2].find("a")["href"]
            doc_url = f"https://www.sec.gov{doc_href}"
            # Download the primary financial report document
            print(doc_url)
            response_doc = requests.get(doc_url, headers=HEADERS)
            os.makedirs(download_dir, exist_ok=True)

            file_name = os.path.join(download_dir, f"filing_{filing_date.strftime('%Y-%m-%d')}.html")
            with open(file_name, "wb") as file:
                file.write(response_doc.content)

            print(f"Downloaded: {file_name}")
            break


# Main function to download the latest financial reports for a company
def sec_edgar_10k_reports(ticker, count, download_dir):
    report_type = "10-K"
    cik = get_cik(ticker)
    if not cik:
        print(f"CIK not found for ticker: {ticker}")
        return

    print(f"CIK for {ticker}: {cik}")
    filing_links = get_financial_report_links(cik, report_type, count)

    if not filing_links:
        print(f"No filings found for CIK: {cik}")
        return

    for filing_link, filing_date in filing_links:
        print(f"Downloading {report_type} from: {filing_link} (Date: {filing_date.strftime('%Y-%m-%d')})")
        download_primary_report(filing_link, filing_date, download_dir)




# Function to get a list of all files in a directory
def list_files_in_directory(directory_path):
    # Get list of all files in the specified path (excluding directories)
    return [item for item in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, item))]


# Function to parse HTML files and extract relevant sections
def parse_and_extract_items(file_path, item_wishlist=None):
    json_output = {}

    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'lxml')
        text = soup.get_text(separator="\n", strip=True)

        current_item = ""
        for line in text.split("\n"):
            line = line.replace("\xa0", " ")
            if current_item:
                json_output[current_item] += line
            if re.match(r'^Item\s\d{1,2}[A-Z]?\.', line, re.IGNORECASE):
                item_in_wishlist = False
                if item_wishlist:
                    for item_wish in item_wishlist:
                        if item_wish.lower() in line.lower():
                            item_in_wishlist = True
                            break
                else:
                    item_in_wishlist = True
                if item_in_wishlist:
                    current_item = line
                    json_output[current_item] = ""
                else:
                    current_item = ""
    return remove_shorter_value_keys(json_output)


# Function to remove keys with smaller value lengths when they share the same base key
def remove_shorter_value_keys(item_dict):
    # Dictionary to store the filtered result
    filtered_dict = {}

    # Iterate over all the keys in the dictionary
    for key, value in item_dict.items():
        # Find the base key without extra trailing text (like "Item 1.")
        base_key = re.match(r'Item\s\d{1,2}[A-Z]?\.', key, re.IGNORECASE).group(0)
        # Convert base_key to lowercase for case-insensitive comparison
        base_key_lower = base_key.lower()
        # If the lowercase base_key exists in the lowercase comparison dictionary
        if any(k.lower() == base_key_lower for k in filtered_dict):
            # Find the exact matching key (case-sensitive) from the original dictionary
            matching_key = next(k for k in filtered_dict if k.lower() == base_key_lower)
            # Compare value lengths and replace the value if necessary
            if len(value) > len(filtered_dict[matching_key][1]):  # Compare value lengths
                filtered_dict[matching_key] = (key, value)  # Replace using original case-sensitive key
        else:
            filtered_dict[base_key] = (key, value)  # Add new entry if not found
    # Create a new dictionary with the keys having the longer values
    final_dict = {filtered_dict[base][0]: filtered_dict[base][1] for base in filtered_dict}
    return final_dict


def extract_sec_10k_items(ticker, count=1):
    ticker_dir = os.path.join(BASE_DIR, ticker)
    json_output_dir = os.path.join(ticker_dir, "json")
    os.makedirs(json_output_dir, exist_ok=True)
    item_wishlist = ["Item 1.", "Item 1A.", "Item 3.", "Item 7.", "Item 7A.", "Item 8."]

    ## Download html reports locally in ticker_dir
    sec_edgar_10k_reports(ticker, count, ticker_dir)
    ## Extract Items from each report
    for html_filename in list_files_in_directory(ticker_dir):
        # if "2015" not in html_filename:
        #     continue
        json_filepath = os.path.join(json_output_dir, f"{html_filename.split('.')[0]}.json")
        print("Extracting Items from ", html_filename)
        json_output = parse_and_extract_items(os.path.join(ticker_dir, html_filename), item_wishlist)

        # Write the parsed JSON output to a file
        with open(json_filepath, 'w', encoding='utf-8') as output_file:
            json.dump(json_output, output_file, ensure_ascii=False, indent=4)
        print("Items saved in ", json_filepath)