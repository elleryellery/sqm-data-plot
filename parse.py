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

