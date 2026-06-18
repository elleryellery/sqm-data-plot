import datetime

# File format:
#      UTC Date & Time, Local Date & Time, Temperature, Counts, Frequency, MSAS
#      YYYY-MM-DDTHH:mm:ss.fff;YYYY-MM-DDTHH:mm:ss.fff;Celsius;number;Hz;mag/arcsec^2

time_utc = [] # UTC Date & Time // YYYY-MM-DDTHH:mm:ss.fff
time_local = [] # Local Date & Time // YYYY-MM-DDTHH:mm:ss.fff
temp = [] # Temperature // Celsius
count = [] # Counts // no units
freq = [] # Frequence // Hz
msas = [] # MSAS // mag/arcsec^2

def parse_file(filename):
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
    out = []

    for point in times:
        date, time = point.split('T')
        year, month, day = date.split('-')
        hour, min, sec = time.split(':')

        out.append(datetime.datetime(int(year), int(month), int(day), int(hour), int(min)))

    return out

def get_unique_dates():
    all_dates = format(time_local)
    unique_dates = []
    for time in all_dates:
        if(not time.date() in unique_dates):
            unique_dates.append(time.date())
    return unique_dates

def get_values_by_date(date): # Ensure that datetime.date() object is passed through!
    all_times = format(time_local)
    times, vals = [], []
    for i in range(len(msas)): # TODO: Use binary search instead of linear to increase speed
        if(all_times[i].date() == date):
            times.append(all_times[i])
            vals.append(msas[i])
    return times, vals

def max_quality_over_time():
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
        time.append(max_time)
        print(f'Max quality on {date}: {max_quality} at {max_time.time()}')
    return qualities, time, dates