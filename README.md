# AO3 Scraper Tools

This is a Python-based project for scraping metadata from Archive of Our Own (AO3) works, including both open and restricted-access fanfics.
This project started because I have too many AO3 tabs open and I wanted to save the metadata for them in an excel file or database.
I included a test input csv in input/test_input.csv. You can see the sample output for these URLS in the output folder.

## Features

- Two standalone scripts:
  - `get_workid_meta_openworks.py`: Scrapes open-access AO3 works. For an input csv with an url per line, it outputs a csv with metadata for the work url. The fields currently included in the output are included fields are workid, title, author, summary, rating, fandoms, url
  - `get_workid_meta_restricted.py`: Scrapes restricted works that require login. For an input csv with an url per line, it outputs a csv with metadata for the work url. The fields currently included in the output are included fields are workid, title, author, summary, rating, fandoms, url
- Robust session handling and login flow for AO3
- Automatic retries on network failures
- Checkpointing to avoid re-scraping completed entries
- Output to CSV for easy analysis and reuse

## Setup

Install dependencies (you may want to use a virtual environment):

```bash
pip install requests beautifulsoup4 pandas
```

## Usage

### Open Works Scraper

```bash
python get_workid_meta_openworks.py
```

### Restricted Works Scraper

Make sure to update the `username` and `password` in `get_workid_meta_restricted.py`.

```bash
python get_workid_meta_restricted.py
```

Both scripts expect structured CSV inputs inside an `input/` folder and will write outputs to an `output/` folder.

## Credits

This project builds on the excellent original AO3 scraper by [@alexwlchan](https://github.com/alexwlchan). Thanks @alexwlchan! 
Some parts of this code were developed with the help of ChatGPT (June 2025), particularly around login handling and error retries.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
