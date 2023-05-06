from collections import Counter
import googlemaps
from datetime import datetime
from geograpy import extraction
import geocoder

"""
Geocoding Concatenator
GeoConcat
Concat a standardized geo column to the dataset
"""

__author__ = "Eden Wu"
__copyright__ = "Copyright (C) 2023 TeamHoWan"
__version__ = "1.0"

class GeoConcat():
    def __init__(self, key):
        self._key = key
        self.gmaps = googlemaps.Client(key=key)
        
    def convert_geocode_to_longlat(self, geocode_result):
        return (geocode_result[0]['geometry']['location']['lng'], geocode_result[0]['geometry']['location']['lat'])
        
    def geocoding(self, string):
        # Geocoding an address
        geocode_result = self.gmaps.geocode(string)
        if geocode_result == []:
            return None
        return self.convert_geocode_to_longlat(geocode_result)
    
    def geocoding_all(self, string):
        geocode_result = self.gmaps.geocode(string)
        if geocode_result == []:
            return None
        return geocode_result
        
        
        
    def read_address(self, input_line):
        """Read Address
        Use geograpy3 Extractor to sementically extract spatial terms.
        Looking up the address of the result using google geocoder.
        Filter out the results with empty city/state.
        """
        e = extraction.Extractor(text=input_line)
        e.find_geoEntities()
        print(e.places)
        
        lookup_res = [geocoder.google(p, key=self._key).current_result for p in e.places]
        lookup_res = [i for i in lookup_res if i is not None]
        lookup_res = [res for res in lookup_res if res.state is not None or res.city is not None]
        if lookup_res == []:
            return None
        
        # Use Counter to count the most common city/state
        lookup_res_count_states = [x.state for x in lookup_res]
        state = Counter(lookup_res_count_states).most_common(1)[0][0]
        lookup_res = [res for res in lookup_res if res.state == state]
        lookup_res_count_cities = [x.city for x in lookup_res]
        city = Counter(lookup_res_count_cities).most_common(1)[0][0]
        
        if city:
            out = geocoder.google(f"{state}, {city}", key=self._key)
        else:
            out = geocoder.google(f"{state} State", key=self._key)
        
        return out

        
    