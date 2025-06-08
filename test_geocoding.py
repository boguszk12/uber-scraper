import os
import time
import json
from dotenv import load_dotenv
from scrape import read_locations, geocode_address, normalize_address

def test_geocoding():
    """
    Test geocoding for all addresses in locations.txt and save results to locations.json
    """
    load_dotenv()
    
    if not os.getenv('GEO_CODE_API_KEY'):
        print("Error: GEO_CODE_API_KEY not found in .env file")
        return
    
    location_pairs = read_locations()
    if not location_pairs:
        print("Error: No locations found in locations.txt")
        return
    
    geocoded_locations = {}
    failed_addresses = []
    
    print("Starting geocoding test...")
    print("-------------------------")
    
    for origin, destination in location_pairs:
        print(f"\nTesting origin: {origin}")
        if origin not in geocoded_locations:
            origin_coords = geocode_address(origin)
            if origin_coords:
                geocoded_locations[origin] = {
                    'latitude': origin_coords['latitude'],
                    'longitude': origin_coords['longitude'],
                    'display_name': origin_coords['display_name']
                }
            else:
                failed_addresses.append(('origin', origin))
        else:
            print(f"Using cached coordinates for: {origin}")
        time.sleep(2)
        
        print(f"Testing destination: {destination}")
        if destination not in geocoded_locations:
            dest_coords = geocode_address(destination)
            if dest_coords:
                geocoded_locations[destination] = {
                    'latitude': dest_coords['latitude'],
                    'longitude': dest_coords['longitude'],
                    'display_name': dest_coords['display_name']
                }
            else:
                failed_addresses.append(('destination', destination))
        else:
            print(f"Using cached coordinates for: {destination}")
        time.sleep(2)
    
    total_addresses = len(location_pairs) * 2
    successful_addresses = len(geocoded_locations)
    failed_count = len(failed_addresses)
    success_rate = (successful_addresses / total_addresses) * 100
    
    print("\nGeocoding Test Results")
    print("---------------------")
    print(f"Total addresses tested: {total_addresses}")
    print(f"Successfully geocoded: {successful_addresses}")
    print(f"Failed to geocode: {failed_count}")
    print(f"Success rate: {success_rate:.2f}%")
    
    if failed_addresses:
        print("\nFailed Addresses:")
        for addr_type, addr in failed_addresses:
            print(f"- {addr} ({addr_type})")
    
    if geocoded_locations:
        with open('locations.json', 'w', encoding='utf-8') as f:
            json.dump(geocoded_locations, f, indent=4, ensure_ascii=False)
        print("\nGeocoded locations saved to: locations.json")
        print(f"Cached {len(geocoded_locations)} unique locations")

if __name__ == "__main__":
    test_geocoding() 