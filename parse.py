import datetime

time_utc = [] # UTC Date & Time // YYYY-MM-DDTHH:mm:ss.fff
time_local = [] # Local Date & Time // YYYY-MM-DDTHH:mm:ss.fff
temp = [] # Temperature // Celsius
count = [] # Counts // no units
freq = [] # Frequence // Hz
msas = [] # MSAS // mag/arcsec^2

def parse_file(filename):
    """
    Reads and parses the specified file according to the following formatting rules:
        UTC Date & Time, Local Date & Time, Temperature, Counts, Frequency, MSAS
        YYYY-MM-DDTHH:mm:ss.fff;YYYY-MM-DDTHH:mm:ss.fff;Celsius;number;Hz;mag/arcsec^2
    
    Args:
        filename (str): The name of the file to be read from.
    """
    print(type(filename))
    with open(filename) as datfile:
        for line in datfile:
            if(line[0] == '#'): # Skip comment lines
                continue

            data = line.split(';') # Split values as specified in file format
            
            time_utc.append(data[0])
            time_local.append(data[1])
            temp.append(data[2])
            count.append(data[3])
            freq.append(data[4])
            msas.append(float(data[5].replace('\n', ''))) # Remove new line indicator from end of line and interpret value as a float

def format(times): # Format UTC or local times as datetime objects so that they can be interpreted and plotted by matplotlib
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

def get_unique_dates():
    """
    Returns a list of unique days that the dataset covers.

    Returns:
        unique_dates (list of datetime objects): First timestamp at which data was recorded on each night.

    """
    all_dates = format(time_local)
    unique_dates = []
    for time in all_dates:
        if(not time.date() in unique_dates):
            unique_dates.append(time.date())
    return unique_dates

def get_values_by_date(date):
    """
    Returns MSAS values and times that were recorded on a specific date.

    Args:
        date (datetime.date() object): The date to get values for. NOTE: Must be datetime.date() object, not datetime!!
    
    Returns:
        times (list of datetime objects): The timestamps at which data was taken throughout the night.
        vals (list of floats): Corresponding MSAS values.
    """
    all_times = format(time_local)
    times, vals = [], []
    for i in range(len(msas)): # TODO: Use binary search instead of linear to increase speed
        if(all_times[i].date() == date):
            times.append(all_times[i])
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
        print(f'Max quality on {date}: {max_quality} at {max_time.time()}') # Debug statement, remove if needed
    
    return qualities, time, dates