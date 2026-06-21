import datetime
from datetime import timedelta
import weather
from zoneinfo import ZoneInfo

time_utc = [] # UTC Date & Time // YYYY-MM-DDTHH:mm:ss.fff
time_local = [] # Local Date & Time // YYYY-MM-DDTHH:mm:ss.fff
temp = [] # Temperature // Celsius
count = [] # Counts // no units
freq = [] # Frequence // Hz
msas = [] # MSAS // mag/arcsec^2

location = weather.Location(0.0, 0.0, "Not specified", "None") # Initial location object with default values

def parse_file(filename):
    """
    Reads and parses the specified file according to the following formatting rules:
        UTC Date & Time, Local Date & Time, Temperature, Counts, Frequency, MSAS
        YYYY-MM-DDTHH:mm:ss.fff;YYYY-MM-DDTHH:mm:ss.fff;Celsius;number;Hz;mag/arcsec^2
    
    Args:
        filename (str): The name of the file to be read from.
    """
    with open(filename) as datfile:

        for line in datfile:
            if(line[0] == '#'):
                if('Location name' in line):
                    location.set_name(line.split(': ')[1].replace('\n', ''))
                elif('Position' in line):
                    position_data = line.split(': ')[1].split(',')

                    location.set_lat(position_data[0])
                    location.set_long(position_data[1])
                elif('Local timezone' in line):
                    location.set_timezone(line.split(': ')[1].replace('\n', ''))
            
                continue #Skip comment lines

            data = line.split(';') # Split values as specified in file format
            
            time_utc.append(format_one(data[0]))
            time_local.append(format_one(data[1]).replace(tzinfo=location.timezone))
            temp.append(data[2])
            count.append(data[3])
            freq.append(data[4])
            msas.append(float(data[5].replace('\n', ''))) # Remove new line indicator from end of line and interpret value as a float

def format_all(times): 
    """
    Formats a list of times from the dataset as datetime objects so that they can be interpreted
    and plotted.

    Args:
        times (list of strings): Times to be formatted -- either UTC or local time values.
    
    Returns:
        out (list of datetime objects): Times converted to datetime objects.
    """
    out = []

    for point in times:
        date, time = point.split('T')
        year, month, day = date.split('-')
        hour, min, sec = time.split(':')

        out.append(datetime.datetime(int(year), int(month), int(day), int(hour), int(min)))

    return out

def format_one(point):
    """
    Formats one point in time as a datetime object to be interpreted and plotted.

    Args:
        point (string): Time to be formatted.
    
    Returns:
        Time converted to datetime object.
    """
    date, time = point.split('T')
    year, month, day = date.split('-')
    hour, min, sec = time.split(':')

    return datetime.datetime(int(year), int(month), int(day), int(hour), int(min))

def get_unique_dates():
    """
    Returns a list of unique days that the dataset covers. Note that the final element in the list will be
    a day with only morning values (i.e. the method returns every single day mentioned in the dataset, not
    every night on which data was taken).

    Returns:
        unique_dates (list of datetime objects): First timestamp at which data was recorded on each night.

    """
    unique_dates = []
    for time in time_local:
        if(not time.date() in unique_dates):
            unique_dates.append(time.date())
    return unique_dates

def get_values_by_date(date):
    """
    Returns MSAS values and times that were recorded on a specific date. "Date" is defined as midnight-to-
    midnight, rather than sunset-to-sunrise or sunrise-to-sunset.

    Args:
        date (datetime.date() object): The date to get values for. NOTE: Must be datetime.date() object, not datetime!!
    
    Returns:
        times (list of datetime objects): The timestamps at which data was taken throughout the night.
        vals (list of floats): Corresponding MSAS values.
    """
    times, vals = [], []
    for i in range(len(msas)): # TODO: Use binary search instead of linear to increase speed
        if(time_local[i].date() == date):
            times.append(time_local[i])
            vals.append(msas[i])
    return times, vals

def get_values_by_night(starttime, endtime):
    """
    Gets values recorded throughout the night between the specified start time and end time.

    Args:
        starttime (datetime object): The start time of the night. Can be a dusk value or a specified time.
        endtime (datetime object): The end time of the night. Can be a dawn value or a specified time.
    
    Returns:
        times (list of datetime objects): The timestamps recorded between the specified start and end times.
        vals (list of floats): The MSAS values recorded between the specified start and end times.
    """
    times, vals = [], []
    for i in range(len(msas)): # TODO: Use binary search instead of linear to increase speed
        if(starttime <= time_local[i] <= endtime):
            times.append(time_local[i])
            vals.append(msas[i])
    return times, vals

def max_quality_over_time():
    """
    Provides data about the best sky quality achieved each night.

    Returns:
        qualities (list of floats): The maximum MSAS values for each night.
        time (list of datetime objects): The time at which the maximum MSAS value was achieved on each night.
        dates (list of datetime objects): The dates for which data was taken.
    """
    dates = get_unique_dates()
    qualities, time = [], []
    for date in dates:

        times, data = get_values_by_date(date)
        max_quality = data[0]
        max_time = times[0]

        for i in range(len(times)):
            if(data[i] > max_quality):
                max_quality = data[i]
                max_time = times[i]
        qualities.append(max_quality)

        if(max_time.hour < 12): # Morning values are pushed to the next day, otherwise the plot will wrap around midnight
            day = 2
        else:
            day = 1

        time.append(datetime.datetime(2026, 1, day, max_time.hour, max_time.minute, max_time.second)) # Normalize times to be within 24 hours of each other for plotting purposes
    
    return qualities, time, dates

def values_dusk_to_dawn():
    """
    Returns the entire dataset filtered by removing datapoints outside of the time between dusk and dawn.
    Can be used for datasets spanning multiple days.

    Returns:
        times_filtered (list of datetime objects): time_local list of timestamps with values outside of dusk-dawn removed.
        msas_filtered (list of floats): msas list of floats with values outside of dusk-dawn removed.
    """
    times_filtered = []
    msas_filtered = []

    dates = get_unique_dates()
    sun_times = {}

    for date in dates:
        data = weather.sun_times(location, date)

        sun_times[f'rise-{date.year}/{date.month}/{date.day}'] = data['dawn']
        sun_times[f'set-{date.year}/{date.month}/{date.day}'] = data['dusk']
    
    for i in range(len(time_local)):
        set = sun_times[f'set-{time_local[i].year}/{time_local[i].month}/{time_local[i].day}']
        rise = sun_times[f'rise-{time_local[i].year}/{time_local[i].month}/{time_local[i].day}']

        if(time_local[i] >= set or time_local[i] <= rise):
            times_filtered.append(time_local[i])
            msas_filtered.append(msas[i])
    
    return times_filtered, msas_filtered

def restricted_values(threshold):
    """
    Returns the dataset with all data points where the MSAS value was less than the specified threshold
    removed.

    Args:
        threshold (float): The minimum MSAS value that the dataset should contain.
    
    Returns:
        times (list of datetime objects): time_local with datapoints below minimum MSAS removed.
        data (list of floats): msas with datapoints below minimum MSAS value removed.
    """
    times, data = [], []

    for i in range(len(time_local)):
        if msas[i] > threshold:
            times.append(time_local[i])
            data.append(msas[i])
    
    return times, data