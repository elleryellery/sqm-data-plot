import astral
from astral.sun import sun
from astral import moon
from zoneinfo import ZoneInfo
import ephem
import requests
import datetime
from datetime import timedelta
import parse

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

def moon_illumination(date):
    return ephem.Moon(date).moon_phase * 100.0

def weather(location, date):
    url = (
    "https://archive-api.open-meteo.com/v1/archive"
    f"?latitude={location.latitude.strip().replace('+', '')}"
    f"&longitude={location.longitude.strip().replace('+', '')}"
    f"&start_date={date}"
    f"&end_date={date + timedelta(days=1)}"
    "&hourly=cloud_cover"
    "&timezone=America/New_York"
    )

    data = requests.get(url).json()

    try:
        times = [t.replace(tzinfo=location.timezone) for t in parse.format_all(data["hourly"]["time"])]
        clouds = data["hourly"]["cloud_cover"]
    except KeyError:
        print(data)
        times, clouds = [], []

    return times, clouds

def bad_day(location, date, verbose=False):
    cloud_cover_threshold = 50.0
    percent_of_night_threshold = 0.5

    sunset = sun_times(location, date)['sunset']
    sunrise = sun_times(location, date + timedelta(days=1))['sunrise']
    if(verbose):
        print(f'Sunrise: {sunset} // Sunset: {sunset}')

    times, clouds = weather(location, date)
    times, clouds = parse.get_values_by_night(times, clouds, sunset - timedelta(minutes=30), sunrise + timedelta(minutes=30))
    num_bad_datapoints = 0

    for point in clouds:
        if point > cloud_cover_threshold:
            num_bad_datapoints += 1

    if(verbose):
        print('/////// DATA //////')
        print(clouds)
    try:
        percent = num_bad_datapoints / float(len(clouds))
        result = percent > percent_of_night_threshold

        if(verbose):
            print('/////// RESULT ///////')
            print(f'{num_bad_datapoints}/{float(len(clouds))} -> {percent} -> {result}')

        return result
    except ZeroDivisionError:
        if(verbose):
            print('Zero Division Error')

        return True
    

def remove_bad_days(data):
    msas, times, dates = data

    filtered_times = []
    filtered_msas = []
    filtered_dates = []

    approved = []
    rejected = []

    for i in range(len(dates)):

        parse.clear_terminal()
        parse.printProgressBar(i, len(dates), 'Removing bad data (this may take several minutes): ', length=40)
        
        sunset = sun_times(parse.location, dates[i])['sunset']
        sunrise = sun_times(parse.location, dates[i] + timedelta(days=1))['sunrise']

        if(times[i].time() <= sunrise.time()):
            date_to_check = dates[i] + timedelta(days=1)
        else:
            date_to_check = dates[i]

        if(not bad_day(parse.location, dates[i])):
            filtered_times.append(times[i])
            filtered_msas.append(msas[i])
            filtered_dates.append(dates[i])
            approved.append(dates[i])
        else:
            rejected.append(dates[i])
    print()
    print(f'Approved ({len(approved)}):')
    for date in approved:
        print(date)
    print()
    print(f'Rejected ({len(rejected)})')
    for date in rejected:
        print(date)
    
    return filtered_msas, filtered_times, filtered_dates