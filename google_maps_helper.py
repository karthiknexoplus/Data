#!/usr/bin/env python3
import urllib.parse
import re

def create_google_maps_link(origin, destination, waypoint=None):
    """
    Creates a Google Maps URL for directions.
    
    Args:
        origin (str): The starting point for the directions.
        destination (str): The final destination.
        waypoint (str, optional): An intermediate point to route through.
    
    Returns:
        str: A direct link to Google Maps with the specified route.
    """
    base_url = "https://www.google.com/maps/dir/"
    
    # URL-encode the location strings to handle spaces and special characters
    encoded_origin = urllib.parse.quote_plus(f"{origin}, Coimbatore")
    encoded_destination = urllib.parse.quote_plus(f"{destination}, Coimbatore")
    
    # Build the path
    if waypoint:
        encoded_waypoint = urllib.parse.quote_plus(f"{waypoint}, Coimbatore")
        path = f"{encoded_origin}/{encoded_waypoint}/{encoded_destination}"
    else:
        path = f"{encoded_origin}/{encoded_destination}"
        
    return f"{base_url}{path}"

def extract_locations_from_ward_description(descriptions):
    """
    Extract location names from ward boundary descriptions.
    
    Args:
        descriptions (list): List of description strings
        
    Returns:
        list: List of extracted location names
    """
    locations = []
    
    # Enhanced location patterns for better extraction
    patterns = [
        # Major landmarks
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Hospital|School|College|Temple|Kovil|Church|Railway Station|Bus Stand|Airport|Market|Mall|Office|Building|Complex|Tower|Plaza|Center|Centre|Museum|Library|Stadium|Ground|Park|Garden|Lake|Pond|Tank|River|Bridge|Gate|Junction|Crossing|Signal|Flyover|Underpass|Overpass))',
        # Residential areas
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Nagar|Colony|Layout|Avenue|Street|Road|Puram|Palayam|Pudur|Thottam|Garden|Extension|Phase|Block|Sector|Ward|Area|Locality|Village|Town|City|District|State))',
        # Directional patterns
        r'towards\s+([^,]+?)(?:\s+via|\s+upto|$)',
        r'from\s+([^,]+?)(?:\s+to|\s+via|\s+upto|$)',
        r'to\s+([^,]+?)(?:\s+via|\s+upto|$)',
        r'via\s+([^,]+?)(?:\s+upto|$)',
        r'upto\s+([^,]+?)(?:\s+via|$)',
        # Infrastructure patterns
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Road|Street|Nagar|Colony|Hospital|Bus Stand|Junction|Office|Avenue|Layout|Thottam|Garden|Nagar|Puram|Palayam|Pudur|Kovil|Temple|School|College|Mill|Bridge|Gate|Station|Terminal|Market|Circle|Square|Park|Ground|Tank|Pond|Canal|River|Flyover|Underpass|Overpass|Signal|Crossing|Level Crossing|Railway|Track|Line))',
    ]
    
    for desc in descriptions:
        for pattern in patterns:
            matches = re.findall(pattern, desc, re.IGNORECASE)
            for match in matches:
                location = match.strip()
                if location and len(location) > 3 and location not in locations:
                    # Clean up the location name
                    location = re.sub(r'\s+', ' ', location)  # Remove extra spaces
                    locations.append(location)
    
    return locations[:8]  # Limit to 8 locations

def create_ward_boundary_map_url(ward_name, direction, descriptions):
    """
    Create a comprehensive Google Maps URL for a ward boundary direction.
    
    Args:
        ward_name (str): Name of the ward
        direction (str): Direction (north, south, east, west)
        descriptions (list): List of boundary descriptions
        
    Returns:
        str: Google Maps URL
    """
    locations = extract_locations_from_ward_description(descriptions)
    
    if len(locations) >= 2:
        # Create directions between first and last location
        origin = locations[0]
        destination = locations[-1]
        waypoints = locations[1:-1] if len(locations) > 2 else None
        
        if waypoints:
            waypoint = waypoints[0]  # Use first waypoint
            return create_google_maps_link(origin, destination, waypoint)
        else:
            return create_google_maps_link(origin, destination)
    elif len(locations) == 1:
        # Single location search
        return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote_plus(locations[0] + ' Coimbatore')}"
    else:
        # Fallback: search for ward area
        return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote_plus(ward_name + ' ' + direction + ' boundary Coimbatore')}"

if __name__ == "__main__":
    # Test with Ward 59 data
    ward_name = "Ward 59"
    direction = "north"
    descriptions = ["from ESI Hospital to East via Neelikonampalayam Road upto Neelikonampalayam Busstand"]
    
    url = create_ward_boundary_map_url(ward_name, direction, descriptions)
    print(f"Generated URL: {url}")
    
    locations = extract_locations_from_ward_description(descriptions)
    print(f"Extracted locations: {locations}")
