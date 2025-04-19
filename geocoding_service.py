import os
import requests
from dotenv import load_dotenv


class GeocodingService:
    """
    A service to geocode location names into latitude and longitude coordinates.
    """

    def __init__(self):
        """
        Initialize the GeocodingService with API key from .env.
        Using OpenCage Geocoding API.
        """
        load_dotenv()
        self.api_key = os.getenv('OPENCAGE_API_KEY')
        self.base_url = "https://api.opencagedata.com/geocode/v1/json"

        if not self.api_key:
            raise ValueError("OpenCage API key not found in environment variables (.env).")

    def geocode(self, location: str):
        """
        Geocode a location name into latitude and longitude.

        Args:
            location (str): The location name to geocode.

        Returns:
            dict: A dictionary with 'latitude', 'longitude', and 'formatted_address'.
        """
        params = {
            'q': location,
            'key': self.api_key,
            'limit': 1,
            'no_annotations': 1
        }

        response = requests.get(self.base_url, params=params)

        if response.status_code != 200:
            raise Exception(f"Geocoding API request failed with status code {response.status_code}")

        data = response.json()

        if not data['results']:
            return None

        result = data['results'][0]

        return {
            "latitude": result['geometry']['lat'],
            "longitude": result['geometry']['lng'],
            "formatted_address": result['formatted']
        }


# Example usage
if __name__ == "__main__":
    service = GeocodingService()

    location = "Los Angeles, USA"
    coordinates = service.geocode(location)

    if coordinates:
        print(f"Location: {coordinates['formatted_address']}")
        print(f"Latitude: {coordinates['latitude']}")
        print(f"Longitude: {coordinates['longitude']}")
    else:
        print("Location not found.")
