import astral
from astral.sun import sun
from astral import moon
from zoneinfo import ZoneInfo

# This file is for handling information about the weather. It also holds the Location class because
# we really only need location data so that we can get weather information.

class Location:
    """
    A class for storing data about the location where the data was taken. Not going to bother
    describing each parameter -- they are pretty self explanatory.
    """
    def __init__(self, latitude, longitude, name, timezone):
        self.latitude = latitude
        self.longitude = longitude
        self.name = name
        self.timezone = timezone
    
    def set_lat(self, latitude):
        self.latitude = latitude

    def set_long(self, longitude):
        self.longitude = longitude

    def set_name(self, name):
        self.name = name 
    
    def set_timezone(self, timezone):
        self.timezone = ZoneInfo(timezone) # Because it will be upset if it's just a string
    
    def out(self): #For quickly printing out information about the location.
        print(f'Location: {self.name} (Lat {self.latitude} / Long {self.longitude} / Time: {self.timezone})')
    

def sun_times(location, date):
    """
    Returns a dictionary with times of important solar events on a specified day.
    NOTE: Only works within United States. Don't know why we'd need it otherwise.
    
    Args:
        location (weather.Location object): The location at which to find sun data.
        date (date.date() object): The date to call sun data for.

    Returns:
        sun_data (dictionary of datetime objects): A dictionary containing important solar events. Available keys are:
            "dawn", "dusk", "noon", "sunrise", "sunset"
    """
    # Uses Astral API to get sun event data
    astral_loc = astral.LocationInfo(location.name, 'United States', location.timezone, location.latitude, location.longitude)

    sun_data = sun(astral_loc.observer, date=date, tzinfo=astral_loc.timezone)

    return sun_data

def moon_times(location, date):
    """
    Returns a dictionary with times of important lunar events on a specified day.
    NOTE: Only works within United States. Don't know why we'd need it otherwise.
    
    Args:
        location (weather.Location object): The location at which to find moon data.
        date (date.date() object): The date to call moon data for.

    Returns:
        sun_data (dictionary of datetime objects): A dictionary containing important solar events. Available keys are:
            "moonrise", "moonset"
    """
    # Uses Astral API to get moon event data
    astral_loc = astral.LocationInfo(location.name, 'United States', location.timezone, location.latitude, location.longitude)

    moon_data = {}

    # Try/Except blocks are because Astral will through a ValueError if a day doesn't have a moonset or moonrise.
    try:
        moon_data['moonrise'] = moon.moonrise(astral_loc.observer, date=date, tzinfo=astral_loc.timezone)
    except ValueError:
        pass

    try:
        moon_data['moonset'] = moon.moonset(astral_loc.observer, date=date, tzinfo=astral_loc.timezone)     
    except ValueError:
        pass

    return moon_data