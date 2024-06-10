Qantas Hotel Scraper
=====================

This script is designed to scrape room rate data from the Qantas Hotels website. Due to active anti-scraping measures on the site, the Playwright library is used instead of Requests. The script includes cursor movements to simulate a real user visiting the site. Additionally, a hidden API was found and utilized to retrieve the necessary data and to bypass protection.

Features
--------

- Scrapes room rate data including room name, rate name, number of guests, cancellation policy, price, whether it's a top deal, and currency.
- Generates check-in and check-out dates.
- Saves data in JSON and CSV formats.

Requirements
------------

The following libraries are required:

- asyncio
- random
- playwright
- json
- csv
- datetime
- urllib.parse
- os

Installation
------------

1. Clone the repository:

   git clone <repository_url>

2. Navigate to the project directory:

   cd <repository_directory>

3. Install the required packages:

   pip install -r requirements.txt

Usage
-----

To run the script, execute the following command:

python script.py

The script will perform the following actions:

1. Navigate to the Qantas Hotels webpage.
2. Simulate random cursor movements to mimic real user behavior.
3. Capture network responses to extract room rate data via the hidden API.
4. Save the extracted data to `rates.json`.
5. Generate check-in and check-out dates and save them to `Checkin_Checkout/checkin_checkout_dates.csv`.



