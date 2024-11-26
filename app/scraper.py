import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# Base URL for the obituaries list
base_url = "https://windsorstar.remembering.ca"
csv_file = "data.csv"
stop_flag_file = "stop_flag.txt"

# Function to get the list of obituaries and extract the detail page links
def get_obituaries_list(page_url):
    response = requests.get(page_url)
    if response.status_code != 200:
        print(f"Failed to fetch list page: {page_url}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    obituary_links = []

    # Find each obituary link on the list page
    for entry in soup.find_all("a", href=True):
        if entry["href"].startswith("/obituary/"):
            obituary_links.append(base_url + entry["href"])

    if not obituary_links:
        print(f"No obituary links found on page: {page_url}")

    return obituary_links

# Function to scrape details from each obituary page
def scrape_obituary_details(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch detail page: {url}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    data = {"URL": url}

    # Keywords for university-related mentions
    university_keywords = ["University of Windsor", "Uwindsor"]
    family_keywords = [
        "father", "mother", "wife", "husband", "son", "daughter", "brother",
        "sister", "child", "children", "grandchild", "grandchildren",
        "family", "survived by"
    ]
    funeral_keywords = ["funeral", "memorial", "visitation", "service", "home", "burial", "interment"]
    donation_keywords = ["donation", "donations", "charity", "memorial contribution"]

    # Extract full name
    name_tag = soup.find("h1", class_="obit-name")
    if name_tag:
        full_name = name_tag.get_text(" ", strip=True)
        data["Full Name"] = full_name

        span_tag = name_tag.find("span", class_="obit-lastname-upper")
        if span_tag:
            last_name = span_tag.get_text(strip=True)
            first_name = full_name.replace(last_name, "").strip()
            data["First Name"] = first_name
            data["Last Name"] = last_name
        else:
            data["First Name"] = full_name
            data["Last Name"] = ""

    # Date of Birth and Date of Death
    dates_tag = soup.find("h2", class_="obit-dates")
    if dates_tag:
        dates = dates_tag.get_text(strip=True).split("-")
        data["Date of Birth"] = dates[0].strip() if len(dates) > 0 else None
        data["Date of Death"] = dates[1].strip() if len(dates) > 1 else None

    # Description and Keyword Extraction
    description_tag = soup.find("p", class_="set-font")
    if description_tag:
        full_description = " ".join(description_tag.stripped_strings)

        # Check for university-related mentions
        university_mention = None
        for keyword in university_keywords:
            if keyword.lower() in full_description.lower():
                university_mention = keyword
                break

        # Skip processing if no university keyword is found
        if not university_mention:
            return None

        # Find all sentences with family mentions
        family_mentions = [
            sentence.strip()
            for sentence in full_description.split(". ")
            if any(keyword in sentence.lower() for keyword in family_keywords)
        ]

        # Extract funeral or memorial service details
        funeral_mentions = [
            sentence.strip()
            for sentence in full_description.split(". ")
            if any(keyword in sentence.lower() for keyword in funeral_keywords)
        ]

        # Extract donation mentions
        donation_mentions = [
            sentence.strip()
            for sentence in full_description.split(". ")
            if any(keyword in sentence.lower() for keyword in donation_keywords)
        ]

        # Extract donation links
        donation_links = [
            a['href'] for a in soup.find_all("a", href=True)
            if "donation" in a['href'].lower() or "charity" in a['href'].lower()
        ]

        # Store Family Mentions
        data["Family Mentions"] = "; ".join(family_mentions) if family_mentions else "N/A"

        # Store Keyword Mentions (University/College)
        data["Keyword Mention"] = university_mention if university_mention else "N/A"

        # Store Full Description
        data["Description"] = full_description

        # Store Funeral or Memorial Details
        data["Funeral Details"] = "; ".join(funeral_mentions) if funeral_mentions else "N/A"

        # Store Donation Mentions
        data["Donation Mentions"] = "; ".join(donation_mentions) if donation_mentions else "N/A"

        # Store Donation Links
        data["Donation Links"] = "; ".join(donation_links) if donation_links else "N/A"
    else:
        return None

    return data



# Function to scrape and store data in a CSV file
def scrape_and_store_obituaries():
    current_page = 1

    while True:
        # Stop scraper if stop flag is set
        if is_scraper_stopped():
            print("Scraper stopped by user.")
            # Clean up the stop flag
            os.remove(stop_flag_file)
            break

        list_page_url = f"{base_url}/obituaries/obituaries/search?&p={current_page}"
        print(f"Fetching obituaries list from page {current_page}: {list_page_url}")

        obituary_links = get_obituaries_list(list_page_url)
        if not obituary_links:
            print(f"No obituaries found on page {current_page}. Ending pagination.")
            break

        all_obituaries = []

        for index, url in enumerate(obituary_links, start=1):
            print(f"Scraping obituary {index}/{len(obituary_links)} on page {current_page}: {url}")
            details = scrape_obituary_details(url)
            if details:
                all_obituaries.append(details)

        if all_obituaries:
            df = pd.DataFrame(all_obituaries)
            mode = 'a' if current_page > 1 else 'w'
            header = current_page == 1
            df.to_csv("data.csv", index=False, mode=mode, header=header)
            print(f"Page {current_page} data saved to 'data.csv'.")

        current_page += 1
        time.sleep(1)

def is_scraper_stopped():
    return os.path.exists(stop_flag_file)