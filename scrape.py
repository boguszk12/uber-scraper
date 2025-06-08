
import functions_framework
import requests
import json
import pickle
import os
import re
import unicodedata
import urllib.parse
import time
from datetime import datetime
import pandas as pd
from google.cloud import storage
from dotenv import load_dotenv
from io import StringIO


load_dotenv()

def normalize_address(address):
    address = address.replace(',', ' ')
    address = unicodedata.normalize('NFKD', address).encode('ASCII', 'ignore').decode('ASCII')
    address = re.sub(r'\s+', ' ', address).strip()
    
    return address

def geocode_address(address):
    normalized_address = normalize_address(address)
    encoded_address = urllib.parse.quote(normalized_address)
    
    api_key = os.getenv('GEO_CODE_API_KEY')
    if not api_key:
        print("Error: GEO_CODE_API_KEY not found in environment variables")
        return None
    
    url = f"https://geocode.maps.co/search?q={encoded_address}&api_key={api_key}"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            if data and len(data) > 0:
                result = data[0]
                
                return {
                    "latitude": float(result.get("lat")),
                    "longitude": float(result.get("lon")),
                    "display_name": result.get("display_name")
                }
            else:
                print("No results found for the given address")
                return None
        else:
            print(f"Error: API request failed with status code {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error occurred during geocoding: {str(e)}")
        return None

def load_uber_cookies():
    json_path = 'uber_cookies.json'
    pkl_path = 'uber_cookies.pkl'
    
    try:
        if os.path.exists(pkl_path):
            print(f"Loading cookies from {pkl_path}")
            with open(pkl_path, 'rb') as f:
                return pickle.load(f)
        elif os.path.exists(json_path):
            print(f"Loading cookies from {json_path}")
            with open(json_path, 'r') as f:
                return json.load(f)
        else:
            print("Cookies file not found. Please run uber_cookies.py first to collect cookies.")
            return None
    except Exception as e:
        print(f"Error loading cookies: {str(e)}")
        return None

def get_uber_prices(origin_coords, destination_coords, cookies):
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,pl-PL;q=0.8,pl;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://m.uber.com',
        'priority': 'u=1, i',
        'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        'x-csrf-token': 'x',
        'x-uber-rv-initial-load-city-id': '939',
        'x-uber-rv-session-type': 'desktop_session',
    }

    json_data = {
        'operationName': 'Products',
        'variables': {
            'includeRecommended': False,
            'destinations': [
                {
                    'latitude': destination_coords['latitude'],
                    'longitude': destination_coords['longitude'],
                },
            ],
            'pickup': {
                'latitude': origin_coords['latitude'],
                'longitude': origin_coords['longitude'],
            },
            'profileType': 'Personal',
        },
        'query': 'query Products($capacity: Int, $destinations: [InputCoordinate!]!, $includeRecommended: Boolean = false, $paymentProfileUUID: String, $pickup: InputCoordinate!, $pickupFormattedTime: String, $profileType: String, $profileUUID: String, $returnByFormattedTime: String, $stuntID: String, $targetProductType: EnumRVWebCommonTargetProductType) {\n  products(\n    capacity: $capacity\n    destinations: $destinations\n    includeRecommended: $includeRecommended\n    paymentProfileUUID: $paymentProfileUUID\n    pickup: $pickup\n    pickupFormattedTime: $pickupFormattedTime\n    profileType: $profileType\n    profileUUID: $profileUUID\n    returnByFormattedTime: $returnByFormattedTime\n    stuntID: $stuntID\n    targetProductType: $targetProductType\n  ) {\n    ...ProductsFragment\n    __typename\n  }\n}\n\nfragment ProductsFragment on RVWebCommonProductsResponse {\n  defaultVVID\n  hourlyTiersWithMinimumFare {\n    ...HourlyTierFragment\n    __typename\n  }\n  intercity {\n    ...IntercityFragment\n    __typename\n  }\n  links {\n    iFrame\n    text\n    url\n    __typename\n  }\n  productsUnavailableMessage\n  tiers {\n    ...TierFragment\n    __typename\n  }\n  __typename\n}\n\nfragment BadgesFragment on RVWebCommonProductBadge {\n  color\n  text\n  __typename\n}\n\nfragment HourlyTierFragment on RVWebCommonHourlyTier {\n  description\n  distance\n  fare\n  fareAmountE5\n  farePerHour\n  minutes\n  packageVariantUUID\n  preAdjustmentValue\n  __typename\n}\n\nfragment IntercityFragment on RVWebCommonIntercityInfo {\n  oneWayIntercityConfig(destinations: $destinations, pickup: $pickup) {\n    ...IntercityConfigFragment\n    __typename\n  }\n  roundTripIntercityConfig(destinations: $destinations, pickup: $pickup) {\n    ...IntercityConfigFragment\n    __typename\n  }\n  __typename\n}\n\nfragment IntercityConfigFragment on RVWebCommonIntercityConfig {\n  description\n  onDemandAllowed\n  reservePickup {\n    ...IntercityTimePickerFragment\n    __typename\n  }\n  returnBy {\n    ...IntercityTimePickerFragment\n    __typename\n  }\n  __typename\n}\n\nfragment IntercityTimePickerFragment on RVWebCommonIntercityTimePicker {\n  bookingRange {\n    maximum\n    minimum\n    __typename\n  }\n  header {\n    subTitle\n    title\n    __typename\n  }\n  __typename\n}\n\nfragment TierFragment on RVWebCommonProductTier {\n  products {\n    ...ProductFragment\n    __typename\n  }\n  title\n  __typename\n}\n\nfragment ProductFragment on RVWebCommonProduct {\n  badges {\n    ...BadgesFragment\n    __typename\n  }\n  cityID\n  currencyCode\n  description\n  detailedDescription\n  discountPrimary\n  displayName\n  estimatedTripTime\n  etaStringShort\n  fares {\n    capacity\n    discountPrimary\n    fare\n    fareAmountE5\n    hasPromo\n    hasRidePass\n    meta\n    preAdjustmentValue\n    __typename\n  }\n  hasPromo\n  hasRidePass\n  hasBenefitsOnFare\n  hourly {\n    tiers {\n      ...HourlyTierFragment\n      __typename\n    }\n    overageRates {\n      ...HourlyOverageRatesFragment\n      __typename\n    }\n    __typename\n  }\n  iconType\n  id\n  is3p\n  isAvailable\n  legalConsent {\n    ...ProductLegalConsentFragment\n    __typename\n  }\n  parentProductUuid\n  preAdjustmentValue\n  productImageUrl\n  productUuid\n  reserveEnabled\n  __typename\n}\n\nfragment ProductLegalConsentFragment on RVWebCommonProductLegalConsent {\n  header\n  image {\n    url\n    width\n    __typename\n  }\n  description\n  enabled\n  ctaUrl\n  ctaDisplayString\n  buttonLabel\n  showOnce\n  shouldBlockRequest\n  __typename\n}\n\nfragment HourlyOverageRatesFragment on RVWebCommonHourlyOverageRates {\n  perDistanceUnit\n  perTemporalUnit\n  __typename\n}\n',
    }

    try:
        response = requests.post(
            'https://m.uber.com/go/graphql', 
            headers=headers, 
            cookies=cookies, 
            json=json_data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: API request failed with status code {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            return None
    except Exception as e:
        print(f"Error occurred during price request: {str(e)}")
        return None

def extract_price_data(raw_data):

    result = []
    
    try:
        tiers = raw_data.get('data', {}).get('products', {}).get('tiers', [])
        
        for tier in tiers:
            tier_title = tier.get('title', '')
            products = tier.get('products', [])
            
            for product in products:
                name = product.get('displayName', '')
                description = product.get('detailedDescription', '')
                eta = product.get('etaStringShort', '')
                estimated_trip_time = product.get('estimatedTripTime', 0)
                
                trip_minutes = int(estimated_trip_time / 60) if estimated_trip_time else 0
                
                fares = product.get('fares', [])
                
                for fare in fares:
                    fare_str = fare.get('fare', '')
                    fare_parts = fare_str.split('\u00a0')
                    currency = fare_parts[0] if len(fare_parts) > 0 else ''
                    fare_value = float(fare_parts[1]) if len(fare_parts) > 1 else 0.0
                    
                    pre_adjustment_str = fare.get('preAdjustmentValue', '')
                    pre_adjustment_parts = pre_adjustment_str.split('\u00a0')
                    pre_adjustment_value = float(pre_adjustment_parts[1]) if len(pre_adjustment_parts) > 1 else 0.0
                    
                    discount = fare.get('discountPrimary', '')
                    has_promo = fare.get('hasPromo', False)
                    capacity = fare.get('capacity', 0)
                    
                    entry = {
                        'tier': tier_title,
                        'name': name,
                        'description': description,
                        'currency': currency,
                        'fare': fare_value,
                        'originalFare': pre_adjustment_value,
                        'discount': discount,
                        'hasPromo': has_promo,
                        'capacity': capacity,
                        'eta': eta,
                        'estimatedTripMinutes': trip_minutes
                    }
                    
                    result.append(entry)
        
        return result
    
    except Exception as e:
        print(f"Error extracting price data: {str(e)}")
        return []

def save_results(origin, destination, price_data, filename=None):

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"uber_prices_{timestamp}.json"
    
    result = {
        "timestamp": int(time.time()),
        "formatted_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "origin": origin,
        "destination": destination,
        "price_data": price_data
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    
    print(f"Results saved to {filename}")

def read_locations(filename='locations.txt'):

    locations = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    origin, destination = line.split(':')
                    locations.append((origin.strip(), destination.strip()))
        return locations
    except Exception as e:
        print(f"Error reading locations file: {str(e)}")
        return []

def clean_fare(fare_str):
    """Helper function to clean fare strings and extract numeric value"""
    if not fare_str:
        return 0.0
    fare_str = str(fare_str).replace('\xa0', ' ')
    fare_str = ''.join(c for c in fare_str if c.isdigit() or c == '.')
    try:
        return float(fare_str)
    except ValueError:
        print(f"Warning: Could not parse fare value: {fare_str}")
        return 0.0
    

def format_price_data_for_csv(origin, destination, raw_data):

    formatted_data = []
    try:
        tiers = raw_data.get('data', {}).get('products', {}).get('tiers', [])
        
        for tier in tiers:
            
            products = tier.get('products', [])
            
            for product in products:
                #print(product)  # Debug print

                eta_raw = product.get('etaStringShort', '')
                eta = eta_raw.split(' ')[-1] if eta_raw else ''
                
                fares = product.get('fares', [{}])[0]
                fare = clean_fare(fares.get('fare', '0'))
   
                row = {
                    'origin': origin,
                    'destination': destination,
                    'tier': tier.get('title', ''),
                    'name': product.get('displayName', ''),
                    'description': product.get('description', ''),
                    'currency': product.get('currencyCode', ''),
                    'fare': fare,
                    'originalFare': clean_fare(fares.get('preAdjustmentValue', fare)),
                    'discount': fares.get('discountPrimary', ''),
                    'hasPromo': fares.get('hasPromo', False),
                    'capacity': fares.get('capacity', 0),
                    'eta': eta,
                    'estimatedTripMinutes': product.get('estimatedTripTime', 0)
                }
                formatted_data.append(row)
                
    except Exception as e:
        print(f"Error formatting price data: {str(e)}")
    
    return formatted_data

def setup_gcs_client():

    try:
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_path and os.path.exists(credentials_path):
            print(f"Using credentials from: {credentials_path}")
            return storage.Client()
        
        print("Error: Google Cloud credentials not found. Please ensure one of the following:")
        print("1. Set GOOGLE_APPLICATION_CREDENTIALS environment variable to point to your service account key file")
        print("2. Place service-account-key.json in the current directory")
        print("3. Run 'gcloud auth application-default login' to set up application default credentials")
        return None
        
    except Exception as e:
        print(f"Error setting up GCS client: {str(e)}")
        return None

def upload_to_gcs(bucket_name, data_frame, destination_blob_name):

    try:
        storage_client = setup_gcs_client()
        if not storage_client:
            return False
            
        buckets = list(storage_client.list_buckets())
        bucket_names = [bucket.name for bucket in buckets]
        
        if bucket_name not in bucket_names:
            print(f"\nError: Bucket '{bucket_name}' not found!")
            print("\nAvailable buckets in your project:")
            for name in bucket_names:
                print(f"- {name}")
            print("\nPlease update your GCS_BUCKET_NAME in .env to one of these bucket names.")
            return False
            
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        csv_buffer = StringIO()
        data_frame.to_csv(csv_buffer, index=False)
        
        blob.upload_from_string(csv_buffer.getvalue(), content_type='text/csv')
        
        print(f"Data uploaded to gs://{bucket_name}/{destination_blob_name}")
        return True
        
    except Exception as e:
        if "403" in str(e):
            print("\nError: Permission denied. Please check that your service account has the following roles:")
            print("- Storage Object Creator (storage.objects.create)")
            print("- Storage Object Viewer (storage.objects.get)")
            print("- Storage Bucket Viewer (storage.buckets.get)")
        elif "404" in str(e):
            print("\nError: Resource not found. Please check your bucket name and permissions.")
        else:
            print(f"\nError uploading to GCS: {str(e)}")
        return False

def get_coordinates(address, cached_locations=None):

    if cached_locations and address in cached_locations:
        print(f"Using cached coordinates for: {address}")
        return cached_locations[address]
    
    print(f"Geocoding address: {address}")
    return geocode_address(address)

def start():

    print("Starting Uber price collector")
    print("--------------------------")
    
    required_env_vars = ['GEO_CODE_API_KEY', 'GCS_BUCKET_NAME']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file")
        return
    
    cookies = load_uber_cookies()
    if not cookies:
        return
    
    cached_locations = {}
    if os.path.exists('locations.json'):
        try:
            with open('locations.json', 'r', encoding='utf-8') as f:
                cached_locations = json.load(f)
            print(f"Loaded {len(cached_locations)} cached locations from locations.json")
        except Exception as e:
            print(f"Warning: Could not load locations.json: {str(e)}")
    
    locations = read_locations()
    if not locations:
        print("No locations found in locations.txt")
        return
    
    timestamp = int(time.time())
    formatted_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"{timestamp}_{formatted_datetime}.csv"
    
    all_price_data = []
    
    for origin_addr, dest_addr in locations:
        print(f"\nProcessing route: {origin_addr} -> {dest_addr}")
        
        origin_coords = get_coordinates(origin_addr, cached_locations)
        if not origin_coords:
            print(f"Could not get coordinates for origin address: {origin_addr}")
            continue
            
        dest_coords = get_coordinates(dest_addr, cached_locations)
        if not dest_coords:
            print(f"Could not get coordinates for destination address: {dest_addr}")
            continue
        
        raw_data = get_uber_prices(origin_coords, dest_coords, cookies)
        if not raw_data:
            print("Failed to get price data")
            continue
        
        formatted_data = format_price_data_for_csv(origin_addr, dest_addr, raw_data)
        all_price_data.extend(formatted_data)
        
        #time.sleep(2)
    
    if all_price_data:
        df = pd.DataFrame(all_price_data)
        #df.to_csv(csv_filename, index=False)
        
        bucket_name = os.getenv('GCS_BUCKET_NAME')
        upload_to_gcs(bucket_name,df,f"2025/{csv_filename}")
    else:
        print("No price data collected")
    
    return

# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def main(arg):
    start()
    return