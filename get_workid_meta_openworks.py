"""
AO3 Scraper for open works with automatic retries and checkpointing.
Does not work with restricted works as those require session login

Connection is finicky but not as bad as when scraping restricted works.
For this reason restricted works are scraped with a different script that uses session login.
Because of connection errors I added checkpointing.

If you get a lot of Connection Errors you can try running outside of peak hours for AO3 and running in batches.

Input

* a csv with urls
* a csv called scraped.csv with the previously scraped workids
* a csv called restricted_ids.csv with a list of the restricted works so we skip them and not try to scrape them with this script

Output

* a csv called scraped.csv with scraped metadata for the URLs, included fields are workid, title, author, summary, rating, fandoms, url. If you want to add more fields modify works.py
* a csv called restricted_ids.csv with a list of the restricted works that were removed from the input list and not scraped

"""

import os
import re
import time
import json
import random
import pandas as pd
import csv

from myao3api import AO3
from myao3api.works import RestrictedWork
from requests.exceptions import ConnectionError

# === Load input and new work IDs ===
# Read new input URLs
with open('input/test_input.csv', 'r') as f:
    import_list = f.readlines()

# Extract work IDs from URLs
pattern = re.compile(r'works/(\d{4,})')
id_matches = [re.findall(pattern, text) for text in import_list]
flattened = [item[0] for item in id_matches if item]
new_ids = sorted(set(flattened))
print("Input import list size:", len(new_ids), "after dedup")
print(new_ids)

# === Load previously completed work IDs ===
def get_completed_ids(filepath='output/scraped.csv'):
    if not os.path.exists(filepath):
        return set()
    df = pd.read_csv(filepath)
    return set(df['workid'].astype(str))

completed_ids = get_completed_ids()
new_ids = [x for x in new_ids if x not in completed_ids]
print("After removing already scraped IDs:", len(new_ids))

# === Load restricted work IDs, remove for now ===
def get_prev_restricted_ids(filepath='output/restricted_ids.csv'):
    if not os.path.exists(filepath):
        return set()
    df = pd.read_csv(filepath)
    return set(df['workid'].astype(str))

prev_restricted_ids = get_prev_restricted_ids()
new_ids = [x for x in new_ids if x not in prev_restricted_ids]
print("After removing prev restricted IDs:", len(new_ids))

# === Write to CSV incrementally ===
def write_json_row(data, filename='output/scraped.csv'):
    fieldnames = ['workid', 'title', 'author', 'summary', 'rating', 'fandoms', 'url']
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow(data)

# === Scraping logic with retries ===
api = AO3()
restricted_ids = []
errored_ids = []

def get_json(work_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            work = api.work(id=str(work_id))
            time.sleep(random.uniform(1.5, 3.0))
            return json.loads(work.json())
        except RestrictedWork:
            print(f"[Restricted] {work_id}")
            restricted_ids.append(work_id)
            return None
        except (ConnectionError, RuntimeError) as e:
            print(f"[Attempt {attempt + 1}] Error for {work_id}: {e}")
            if attempt < max_retries - 1:
                wait = random.uniform(5, 15)
                print(f"Retrying in {wait:.1f} seconds...")
                time.sleep(wait)
            else:
                errored_ids.append(work_id)
                return None

# === Main scraping loop ===
for i, work_id in enumerate(new_ids[0:15]):
    print(f"Scraping {i+1}/{len(new_ids)}: {work_id}")
    result = get_json(work_id)
    if result:
        write_json_row(result)

# === Save restricted and errored logs ===
pd.Series(restricted_ids, name='workid').to_csv('output/restricted_ids.csv', index=False)
pd.Series(errored_ids, name='workid').to_csv('output/errored_ids.csv', index=False)