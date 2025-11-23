#!/usr/bin/env python3
"""
Get altitude/elevation for specific GPS coordinates

Usage:
    python3 get_altitude.py <latitude> <longitude>
    python3 get_altitude.py 50.518294 30.518004

Or use from URL:
    python3 get_altitude.py --url "https://maps.apple.com/frame?center=50.518294,30.518004&..."
"""

import sys
import json
import urllib.request
import urllib.parse
import re
import argparse

def parse_url(url):
    """Extract coordinates from Apple Maps URL"""
    # Extract center parameter
    match = re.search(r'center=([\d.]+),([\d.]+)', url)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None

def get_altitude_open_elevation(latitude, longitude):
    """Get altitude using Open-Elevation API (free, no API key required)"""
    url = "https://api.open-elevation.com/api/v1/lookup"
    data = {
        "locations": [
            {"latitude": latitude, "longitude": longitude}
        ]
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get('results') and len(result['results']) > 0:
                elevation = result['results'][0].get('elevation')
                return {
                    "latitude": latitude,
                    "longitude": longitude,
                    "altitude": elevation,
                    "source": "open-elevation",
                    "success": True
                }
    except Exception as e:
        return {
            "error": f"Open-Elevation API error: {str(e)}",
            "success": False
        }
    
    return {
        "error": "No elevation data returned",
        "success": False
    }

def get_altitude_google_elevation(latitude, longitude, api_key=None):
    """Get altitude using Google Elevation API (requires API key)"""
    if not api_key:
        return {
            "error": "Google Elevation API requires an API key",
            "success": False
        }
    
    url = "https://maps.googleapis.com/maps/api/elevation/json"
    params = {
        "locations": f"{latitude},{longitude}",
        "key": api_key
    }
    
    try:
        full_url = f"{url}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(full_url, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get('status') == 'OK' and result.get('results'):
                elevation = result['results'][0].get('elevation')
                return {
                    "latitude": latitude,
                    "longitude": longitude,
                    "altitude": elevation,
                    "source": "google-elevation",
                    "success": True
                }
            else:
                return {
                    "error": f"Google API error: {result.get('status', 'Unknown error')}",
                    "success": False
                }
    except Exception as e:
        return {
            "error": f"Google Elevation API error: {str(e)}",
            "success": False
        }

def get_altitude_usgs(latitude, longitude):
    """Get altitude using USGS Elevation Point Query Service (free, US only)"""
    url = "https://epqs.nationalmap.gov/v1/xml"
    params = {
        "x": longitude,
        "y": latitude,
        "units": "Meters",
        "output": "json"
    }
    
    try:
        full_url = f"{url}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(full_url, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if 'value' in result:
                elevation = result['value']
                return {
                    "latitude": latitude,
                    "longitude": longitude,
                    "altitude": elevation,
                    "source": "usgs",
                    "success": True
                }
    except Exception as e:
        return {
            "error": f"USGS API error: {str(e)}",
            "success": False
        }
    
    return {
        "error": "No elevation data returned from USGS",
        "success": False
    }

def get_altitude(latitude, longitude, api_key=None):
    """
    Get altitude for coordinates, trying multiple services
    """
    # Try Open-Elevation first (free, worldwide, no API key)
    result = get_altitude_open_elevation(latitude, longitude)
    if result.get("success"):
        return result
    
    # If Open-Elevation fails and we have a Google API key, try Google
    if api_key:
        result = get_altitude_google_elevation(latitude, longitude, api_key)
        if result.get("success"):
            return result
    
    # For US coordinates, try USGS as fallback
    if 24.0 <= latitude <= 50.0 and -125.0 <= longitude <= -66.0:
        result = get_altitude_usgs(latitude, longitude)
        if result.get("success"):
            return result
    
    return {
        "error": "Could not retrieve altitude from any service",
        "success": False
    }

def main():
    parser = argparse.ArgumentParser(
        description="Get altitude/elevation for GPS coordinates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 get_altitude.py 50.518294 30.518004
  python3 get_altitude.py --url "https://maps.apple.com/frame?center=50.518294,30.518004&..."
  python3 get_altitude.py 50.518294 30.518004 --api-key YOUR_GOOGLE_API_KEY
        """
    )
    
    parser.add_argument('latitude', nargs='?', type=float, help='Latitude')
    parser.add_argument('longitude', nargs='?', type=float, help='Longitude')
    parser.add_argument('--url', type=str, help='Apple Maps URL to extract coordinates from')
    parser.add_argument('--api-key', type=str, help='Google Elevation API key (optional)')
    parser.add_argument('--json', action='store_true', help='Output only JSON')
    
    args = parser.parse_args()
    
    # Parse URL if provided
    if args.url:
        lat, lon = parse_url(args.url)
        if lat is None or lon is None:
            print(json.dumps({
                "error": "Could not parse coordinates from URL",
                "success": False
            }), file=sys.stderr)
            sys.exit(1)
        latitude, longitude = lat, lon
    elif args.latitude is not None and args.longitude is not None:
        latitude, longitude = args.latitude, args.longitude
    else:
        parser.print_help()
        sys.exit(1)
    
    # Validate coordinates
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        print(json.dumps({
            "error": "Invalid coordinates. Latitude must be -90 to 90, longitude -180 to 180",
            "success": False
        }), file=sys.stderr)
        sys.exit(1)
    
    # Get altitude
    result = get_altitude(latitude, longitude, args.api_key)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            print(json.dumps(result, indent=2))
            print(f"\nCoordinates: {result['latitude']}, {result['longitude']}")
            print(f"Altitude: {result['altitude']} meters")
            print(f"Source: {result.get('source', 'unknown')}")
        else:
            print(json.dumps(result, indent=2), file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()

