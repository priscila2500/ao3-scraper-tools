"""
AO3 Scraper for Restricted Works with AO3 login, retries, and checkpointing
Working version as of June 2025

Input AO3 username and password in the code down below to access restricted works.

Connection is finicky. Try several times until it runs.
Also, try running outside of peak hours for AO3.

In a bad day this script works 1 out of 10 times it's submitted.

The following are errors you can ignore and retry.

* Login failed — still not recognized as logged in.
* TypeError: 'NoneType' object is not subscriptable.

Input

* a csv with urls
* a csv called restricted_ids with the previously scraped workids
* a csv called scraped_restricted.csv with a list of the restricted works so we skip them and not try to scrape them

Output

* a csv called scraped_restricted.csv with scraped metadata for the URLs. included fields are workid, title, author, summary, rating, fandoms, url. If you want to add more fields modify works.py

TODO: Title field does not seem to import correctly for restricted works. Will have to fix later.

"""

import os
import time
import json
import random
import pandas as pd
import csv
import requests
from bs4 import BeautifulSoup

from myao3api.works import Work, RestrictedWork
from requests.exceptions import ConnectionError


## === LOGIN FOR RESTRICTED IDS FUNCTIONS === ##
# === Credentials ===
username = ' ' #type username here
password = ' rr' #type password here

# === Ensure output dir exists ===
os.makedirs('output', exist_ok=True)


# === AO3 login function that works as of Jun 2025 ===
def ao3_login(username, password):
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0",
    }

    # Step 1: Go to homepage first to set initial cookies
    session.get("https://archiveofourown.org", headers=headers)

    # Step 2: Go to login page to get token
    res = session.get("https://archiveofourown.org/users/login", headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    token = soup.find("input", {"name": "authenticity_token"})["value"]

    # Step 3: Post login with correct fields
    login_data = {
        "authenticity_token": token,
        "user[login]": username,
        "user[password]": password,
    }

    login_res = session.post(
        "https://archiveofourown.org/users/login",
        data=login_data,
        headers=headers,
    )

    # Step 4: Confirm login
    confirm = session.get("https://archiveofourown.org/", headers=headers)
    if f"/users/{username}" in confirm.text or 'logged-in' in confirm.text:
        print("✅ Login successful and recognized!")
        return session
    else:
        with open("login_debug_final.html", "w", encoding="utf-8") as f:
            f.write(confirm.text)
        raise RuntimeError("🚫 Login failed — still not recognized as logged in.")

## === DATA LOADING AND OUTPUT WRITING FUNCTIONS === ##
# === Load input restricted work IDs from file ===
def get_input_ids(filepath='output/restricted_ids.csv'):
    if not os.path.exists(filepath):
        print("⚠️  Input file not found:", filepath)
        return set()
    df = pd.read_csv(filepath)
    return set(df['workid'].astype(str))

# === Load already scraped restricted work IDs from file ===
def get_prev_scraped_ids(filepath='output/scraped_restricted.csv'):
    if not os.path.exists(filepath):
        print("⚠️  Input file not found:", filepath)
        return set()
    df = pd.read_csv(filepath)
    return set(df['workid'].astype(str))

# === Write to CSV incrementally ===
def write_json_row(data, filename='output/scraped_restricted.csv'):
    fieldnames = ['workid', 'title', 'author', 'summary', 'rating', 'fandoms', 'url']
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow(data)

## === MAIN SCRAPING LOGIC FUNCTION=== ##
errored_ids = []

def get_json(work_id, session, max_retries=3):
    for attempt in range(max_retries):
        try:
            work = Work(id=str(work_id), sess=session)
            time.sleep(random.uniform(1.5, 3.0))
            return json.loads(work.json())
        except RestrictedWork as e:
            #This shouldn't happen if logged correctly
            print(f"❌ Restricted access for {work_id}: {e}")
            restricted_ids.append(work_id)
            return None
        except (ConnectionError, RuntimeError) as e:
            print(f"[Attempt {attempt + 1}] Error for {work_id}: {e}")
            if attempt < max_retries - 1:
                wait = random.uniform(5, 15)
                print(f"🔁 Retrying in {wait:.1f} seconds...")
                time.sleep(wait)
            else:
                errored_ids.append(work_id)
                return None


# === Main ===
if __name__ == "__main__":
    session = ao3_login(username, password)

    input_ids = get_input_ids()
    prev_scraped_ids=get_prev_scraped_ids()
    new_ids = [x for x in input_ids if x not in prev_scraped_ids]

    print(f"📥 {len(input_ids)} work IDs in input list.")
    print("After removing already scraped IDs:", len(new_ids))

    for i, work_id in enumerate(new_ids):
        print(f"\n🔎 Scraping {i+1}/{len(new_ids)}: {work_id}")
        result = get_json(work_id, session)
        if result:
            write_json_row(result)

    print("\n✅ Done.")