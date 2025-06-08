# UberScraper

A Python-based tool for scraping Uber ride prices between specified locations. This project allows you to collect and analyze Uber pricing data, with support for geocoding addresses and storing results in Google Cloud Storage.

## Features

- Scrape real-time Uber prices between locations
- Geocoding support for converting addresses to coordinates
- Support for multiple ride types and price tiers
- Data export to CSV format
- Google Cloud Storage integration
- Cookie-based authentication for reliable scraping

## Prerequisites

- Python 3.7 or higher
- Google Cloud account (for storage features)
- Geocoding API key from maps.co
- Chrome browser installed (for Selenium)
- ChromeDriver matching your Chrome version

## Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
cd uberscraper_cleaned
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```
GEO_CODE_API_KEY=your_geocoding_api_key
GCS_BUCKET_NAME=bucket-name
GOOGLE_APPLICATION_CREDENTIALS=path-to-creds-json
```

4. Set up Google Cloud credentials:
- Place your Google Cloud service account key file in the project root
- Name it `X.json` or update the reference in the code

## Setup Process

### 1. Configure Location Data
First, create a `locations.txt` file with your desired routes:
```
address1:address2
address3:address4
```

### 2. Run Geocoding Test
Run the geocoding test to validate your locations and create the required `locations.json` file:
```bash
python test_geocoding.py
```

This script will:
- Test each address in `locations.txt`
- Convert addresses to coordinates using the geocoding API
- Save the results to `locations.json`
- Display success/failure statistics
- Handle rate limiting with appropriate delays

### 3. Set Up Uber Authentication
Run the Uber cookie collector to set up authentication:
```bash
python uber_cookies.py
```

This script will:
1. Open a Chrome browser window
2. Navigate to Uber's login page
3. Wait for you to manually log in (you have 5 minutes)
4. After successful login, automatically:
   - Collect necessary cookies
   - Save them to `uber_cookies.json` and `uber_cookies.pkl`
   - Close the browser

The Chrome session will be saved in the `uber_chrome_profile` directory for future use.

## Usage

After completing the setup process above, you can run the main scraper:
```bash
python scrape.py
```

The script will:
- Load the geocoded locations from `locations.json`
- Use saved cookies for authentication
- Fetch Uber prices for each route
- Save results locally and/or upload to Google Cloud Storage

## Data Format

The scraper collects the following information for each route:
- Tier (e.g., Economy, Premium)
- Ride type name
- Description
- Currency
- Current fare
- Original fare (before discounts)
- Available discounts
- Promotional offers
- Vehicle capacity
- ETA
- Estimated trip duration

## File Structure

- `scrape.py`: Main scraping script
- `uber_cookies.py`: Cookie management for Uber authentication
- `test_geocoding.py`: Tests for the geocoding functionality
- `requirements.txt`: Project dependencies
- `locations.txt`/`locations.json`: Input files for routes to scrape
- `schema.json`: Data schema definition

## Error Handling

The script includes robust error handling for:
- Failed API requests
- Geocoding errors
- Network timeouts
- Invalid addresses
- Authentication issues


## Disclaimer

This tool is for educational purposes only. Please ensure you comply with Uber's terms of service and API usage policies when using this tool. 