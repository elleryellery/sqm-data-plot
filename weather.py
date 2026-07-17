import astral
from astral.sun import sun
from astral import moon
from zoneinfo import ZoneInfo
import ephem
import requests
import datetime
from datetime import timedelta
import parse
import graph
from scipy.integrate import trapezoid
import numpy as np

all_times, all_clouds = [], []

# This file is for handling information about the weather. It also holds the Location class because
# we really only need location data so that we can get weather information.

class Location:
    """
    A class for storing data about the location where the data was taken.
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
        self.timezone = ZoneInfo(timezone)
    
    def out(self):
        """
        Quickly print out information about the location.
        """
        print(f'Location: {self.name} (Lat {self.latitude} / Long {self.longitude} / Time: {self.timezone})')

################################################################################################
################################### MOON AND SUN TIMESTAMPS ####################################
################################################################################################

def sun_times(location, date):
    """
    Returns a dictionary with times of important solar events on a specified day.
    NOTE: Currently only works within the United States.
    
    Args:
        location (weather.Location object): The location at which to find sun data.
        date (date.date() object): The date to call sun data for.

    Returns:
        dictionary of datetime objects: A dictionary containing important solar events. Available keys are:
            "dawn", "dusk", "noon", "sunrise", "sunset"
    """
    # Uses Astral API to get sun event data
    astral_loc = astral.LocationInfo(location.name, 'United States', location.timezone, location.latitude, location.longitude)

    sun_data = sun(astral_loc.observer, date=date, tzinfo=astral_loc.timezone)

    return sun_data

def moon_times(location, date):
    """
    Returns a dictionary with times of important lunar events on a specified day.
    NOTE: Currently only works within the United States.
    
    Args:
        location (weather.Location object): The location at which to find moon data.
        date (date.date() object): The date to call moon data for.

    Returns:
        dictionary of datetime objects: A dictionary containing important solar events. Available keys are:
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

def sunrise(date):
    """
    Returns a datetime object representing the sunrise time on a given date.
    """
    return get_all_data(date)['sunrise']

def sunset(date):
    """
    Returns a datetime object representing the sunset time on a given date.
    """
    return get_all_data(date)['sunset']

def dawn(date):
    """
    Returns a datetime object representing the dawn time on a given date.
    """
    return get_all_data(date)['dawn']

def dusk(date):
    """
    Returns a datetime object representing the dusk time on a given date.
    """
    return get_all_data(date)['dusk']

def moonrise(date):
    """
    Returns a datetime object representing the moonrise time on a given date.
    """
    return get_all_data(date)['moonrise']

def moonset(date):
    """
    Returns a datetime object representing the moonset time on a given date.
    """
    return get_all_data(date)['moonset']

def moon_illumination(date):
    """
    Returns the percent illumination of the moon as a float from 0.0-100.0.
    """
    return ephem.Moon(date).moon_phase * 100.0

def get_all_data(date):
    """
    Gets all sun and moon data in a dictionary. Valid keys are: "dusk", "sunset", "dawn",
    "sunrise", "moonset", "moonrise".

    Args:
        date (datetime.date object): date on which the night begins

    Returns:
        dictionary of datetime objects: sun and moon event data
    """

    tomorrow = date + timedelta(days = 1)
    
    sun_data = sun_times(parse.location, date)
    sun_data_tomorrow = sun_times(parse.location, tomorrow)
    moon_data = moon_times(parse.location, date)
    moon_data_tomorrow = moon_times(parse.location, tomorrow)

    all_data = {}
    all_data['dusk'] = sun_data['dusk']
    all_data['sunset'] = sun_data['sunset']
    all_data['dawn'] = sun_data_tomorrow['dawn']
    all_data['sunrise'] = sun_data_tomorrow['sunrise']

    sunrise = all_data['sunrise']
    sunset = all_data['sunset']

    # All of this crazy code is trying to fix the fact that Astral will return data for a day
    # as defined by midnight to midnight rather than data for the night as defined by dusk to
    # dawn, so we have to get some data for the date on which the night starts and some for the
    # date on which the night ends and handle that data accordingly.
    try:
        if(sunset <= moon_data['moonset'] <= sunrise):
            all_data['moonset'] = moon_data['moonset']
        elif(sunset <= moon_data_tomorrow['moonset'] <= sunrise):
            all_data['moonset'] = moon_data_tomorrow['moonset']

    except TypeError: #Handles case where moonrise goes from 11:59 to midnight
        if(sunset <= moon_data_tomorrow['moonset'] <= sunrise):
            all_data['moonset'] = moon_data_tomorrow['moonset']
    except KeyError:
        pass

    try:
        if(sunset <= moon_data['moonrise'] <= sunrise):
            all_data['moonrise'] = moon_data['moonrise']
        elif(sunset <= moon_data_tomorrow['moonrise'] <= sunrise):
            all_data['moonrise'] = moon_data_tomorrow['moonrise']

    except TypeError: #Handles case where moonrise goes from 11:59 to midnight
        if(sunset <= moon_data_tomorrow['moonrise'] <= sunrise):
            all_data['moonrise'] = moon_data_tomorrow['moonrise']
    except KeyError:
        pass

    return all_data

################################################################################################
################################# GETTING WEATHER CONDITIONS ###################################
################################################################################################

def weather(location, date):
    """
    Returns forecasted cloud cover for a given date and location using the OpenMeteo API. Note that
    each request takes several seconds.

    Args:
        location (Location object): the location 

    Returns:
        list of datetime objects: Cloud cover timestamps. These will be hourly.
        list of integers: Forecasted cloud cover percentage from 0-100. The API seems
            to do this in increments no smaller than 10%.
    """

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

def all_weather(location):
    """
    Stores weather forecast for the entire dataset to prevent repeated API calls. This can be
    called when weather information needs to be updated, but should not be used repeatedly
    within loops.

    Args:
        location (Location object): The location to retrieve forecasts for.

    Returns:
        list of datetime objects:
    """
    dates = parse.get_unique_dates(parse.time_local)
    url = (
    "https://archive-api.open-meteo.com/v1/archive"
    f"?latitude={location.latitude.strip().replace('+', '')}"
    f"&longitude={location.longitude.strip().replace('+', '')}"
    f"&start_date={dates[0]}"
    f"&end_date={dates[-1]}"
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

def from_all_weather_night(date):
    """
    Returns weather data for a specified date by referencing the last API call (i.e. the 
    "big_weather" method output). This way, there is no need to make a new API call.

    Returns:
        list of datetime objects: timestamps
        list of integers: cloud cover percentage as an integer (0-100)
    """
    return parse.get_values_by_time(all_times, all_clouds, sunset(date) - timedelta(minutes=30), sunrise(date) + timedelta(minutes=30))

def update_all_weather():
    """
    Update global weather data using all_weather() method (a single API call).
    """
    print("\rUpdating weather data...", end="", flush=True)

    global all_times
    global all_clouds

    all_times, all_clouds = all_weather(parse.location)
    print("Done!")

################################################################################################
################################## WEATHER CONDITION FILTERS ###################################
################################################################################################

def bad_day(date):
    """
    Returns whether a date has bad weather, defined as cloud cover above 50% lasting more than
    50% of the night.

    Returns:
        boolean: whether or not the day has bad weather
    """
    cloud_cover_threshold = 50.0
    percent_of_night_threshold = 0.5

    _, clouds = from_all_weather_night(date)
    num_bad_datapoints = 0

    for point in clouds:
        if point > cloud_cover_threshold:
            num_bad_datapoints += 1

    try:
        percent = num_bad_datapoints / float(len(clouds))
        result = percent > percent_of_night_threshold

        return result
    
    except ZeroDivisionError:
        return True
    
def remove_bad_days(data):
    """
    Filters a dataset by removing bad days (see bad_day() for definition of a bad day).

    Args:
        data (list of floats, list of datetime objects, list of datetime.date objects): 
            msas, timestamps, and dates (respectively)
    
    Returns:
        list of floats: filtered msas values
        list of datetime objects: filtered timestamps
        list of datetime.date objects: filtered dates
    """
    msas, times, dates = data

    filtered_times = []
    filtered_msas = []
    filtered_dates = []

    approved = []
    rejected = []

    for i in range(len(dates)):
        parse.printProgressBar(i, len(dates), 'Removing bad data: ', length=40)
        
        if(not bad_day(dates[i])):
            filtered_times.append(times[i])
            filtered_msas.append(msas[i])
            filtered_dates.append(dates[i])
            approved.append(dates[i])
        else:
            rejected.append(dates[i])
    
    return filtered_msas, filtered_times, filtered_dates

def dim_moon(date):
    """
    Returns whether the moon illumination on a certain date is less than 30%.
    """
    illumination = moon_illumination(date)

    return illumination <= 25.0

def no_moon(date):
    """
    Returns whether the moon has negligible effects on a certain date. Moon is considered negligible
    if either of the following conditions are met:
        - Moon illumination is less than 25%.
        - Moon sets before sunset and rises after sunrise.

    Args:
        date (datetime.date): date to check
    
    Returns:
        boolean: whether either condition for negligible moon conditions are met
    """
    tomorrow = date + timedelta(days=1)
    limit1 = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 2, 0, 0, tzinfo=parse.location.timezone)
    limit2 = datetime.datetime(date.year, date.month, date.day, 23, 30, 0, tzinfo=parse.location.timezone)

    no_moon = True
    no_moonset = False
    no_moonrise = False

    try:
        moonrise_time = moonrise(date)
    except KeyError:
        moonrise_time = datetime.datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=parse.location.timezone)
        no_moonrise = True

    try:
        moonset_time = moonset(date)
    except KeyError:
        moonset_time = datetime.datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=parse.location.timezone)
        no_moonset = True

    try:
        if((moonrise_time <= limit1 or no_moonrise) and (moonset_time >= limit2 or no_moonset)):
            no_moon = False
        
        if(dim_moon(date)):
            no_moon = True
        
    except:
        no_moon = False

    return no_moon


def filter_no_moon(vals, dates):
    """
    Filters a dataset by removing dates where the moon affects MSAS values.

    Args:
        vals (list of floats): MSAS values
        times (list of datetime objects): timestamps
        dates (list of datetime.date objects): dates
    
    Returns:
        list of datetime.date objects: filtered dates
        list of floats: filtered MSAS values
    """
    dates_filtered = []
    vals_filtered = []

    for i in range(len(vals)):
        if(no_moon(dates[i])):
            dates_filtered.append(dates[i])
            vals_filtered.append(vals[i])
            
    return dates_filtered, vals_filtered

def find_moon_effect_references(dates):
    """
    Finds dates that serve as good references for studying the effects of the moon on MSAS values.

    Args:
        vals (list of floats): MSAS values
        dates (list of datetime.date objects): dates to check
    
    Returns:
        list of datetime.date objects: dates that are moon references
    """
    references = []
    for i in range(len(dates)):
        parse.printProgressBar(i, len(dates), 'Searching for moon reference dates: ', length=50)
        date = dates[i]
        if(is_moon_effect_reference(date)):
            references.append(date)

    return references

def is_moon_effect_reference(date):
    """
    Checks whether a date would be a good data point for studying the effect of the moon on MSAS
    values. A good reference point meets the following qualities:
        - Moon rises at some point between sunset and sunrise
        - Night is clear (using the clear_day() method)

    Args:
        date (datetime.date object)

    Returns:
        boolean: whether or not the date would be a good reference date
    """
    try:
        moonrise = moonrise(date)
    except:
        return False
    
    tomorrow = date + timedelta(days=1)
    limit1 = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 2, 0, 0, tzinfo=parse.location.timezone)
    limit2 = datetime.datetime(date.year, date.month, date.day, 22, 0, 0, tzinfo=parse.location.timezone)
    
    if not(limit2 <= moonrise <= limit1):
        return False

    times, clouds = from_all_weather_night(date)

    if(not clear_day(date)):
        return False

    return True
        
def clear_day(date):
    """
    Returns whether a night is considered relatively clear of clouds. Determined by the integral
    of the cloud cover over the whole night.

    Args:
        times (list of datetime objects): timestamps
        clouds (list of floats): cloud cover values

    Returns:
        boolean: whether the night is clear
    """
    times, clouds = from_all_weather_night(date)
    timestamps = np.fromiter((t.timestamp() for t in times), dtype=float)
    clouds[0] = 0
    clouds[-1] = 0
    integral = abs(trapezoid(timestamps, np.array(clouds)))
    threshold = (timestamps[-1] - timestamps[0]) * 20.0
    clear = integral < threshold

    return clear

def no_clouds(date):
    """
    Returns whether the night has no clouds. This is defined as having clouds never exceeding
    15% cloud cover.

    Args:
        date (datetime.date): date to check
    
    Returns:
        boolean: whether the night meets the criteria specified above
    """
    _, clouds = from_all_weather_night(date)
    for point in clouds:
        if(point > 0.15):
            return False
        
    return True
