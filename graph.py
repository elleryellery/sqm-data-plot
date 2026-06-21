import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import parse
import weather
from datetime import timedelta
from zoneinfo import ZoneInfo

# Defines the color of the event marker bars. List of color options can be found here: 
# https://matplotlib.org/stable/gallery/color/named_colors.html
# Feel free to change.
event_colors = {}
event_colors['dawn'] = 'gold'
event_colors['dusk'] = 'mediumpurple'
event_colors['noon'] = 'darkorange'
event_colors['sunrise'] = 'darkgoldenrod'
event_colors['sunset'] = 'rebeccapurple'
event_colors['moonrise'] = 'royalblue'
event_colors['moonset'] = 'cornflowerblue'

msas_night_threshold = 17.0

timeFormat = mdates.DateFormatter('%H:%M')

def update_time_format():
    return mdates.DateFormatter('%H:%M', tz=parse.location.timezone)

def graph_quality(filter_type):
    """
    Graphs the quality over time (i.e. throughout the night) for the entire dataset.

    Args:
        filter_type (str): If you wish to remove daytime values from the graph, you must specify
            a filter type. Options are as follows:
                by value: Removes datapoints where the MSAS is below the msas_night_threshold
                by dawn/dusk: Removes datapoints that are not between dawn and dusk
                none: Keeps all values, including daytime ones.
    """
    plt.figure()

    if(filter_type == 'by value'):
        x, y = parse.restricted_values(msas_night_threshold)
    elif(filter_type == 'by dawn/dusk'):
        x, y = parse.night_time_values()
    elif(filter_type == 'none'):
        x, y = parse.time_local, parse.msas
    else:
        raise TypeError('Unrecognized filter type.')

    plt.plot(x, y) # Plot time on x-axis, MSAS on y-axis

    plt.gca().invert_yaxis() # Flip y-axis upside down as specified by Tim

    plt.xlabel("Time (s)")
    plt.ylabel("MSAS")
    plt.title("MSAS vs Time")
    plt.grid()

    plt.show()

def graph_quality_with_event_markers(filter_type):
    """
    Graphs the entire dataset with markers showing important sun and moon events (i.e. dawn, dusk,
    sunrise, sunset, moonrise, moonset, etc.).

    Args:
        filter_type (str): If you wish to remove daytime values from the graph, you must specify
            a filter type. Options are as follows:
                by value: Removes datapoints where the MSAS is below the msas_night_threshold
                by dawn/dusk: Removes datapoints that are not between dawn and dusk
                none: Keeps all values, including daytime ones.
    """
    plt.figure()

    if(filter_type == 'by value'):
        x, y = parse.restricted_values(msas_night_threshold)
    elif(filter_type == 'by dawn/dusk'):
        x, y = parse.night_time_values()
    elif(filter_type == 'none'):
        x, y = parse.time_local, parse.msas
    else:
        raise TypeError('Unrecognized filter type.')

    plt.plot(x,y) # Plot time on x-axis, MSAS on y-axis

    for date in parse.get_unique_dates(parse.time_local):
        sun_data = weather.sun_times(parse.location, date)
        moon_data = weather.moon_times(parse.location, date)

        for label, time in (sun_data | moon_data).items():
            try:
                plt.axvline(time, color=event_colors[label])
                plt.text(time, (plt.ylim()[0] + plt.ylim()[1])/2, label.capitalize(), rotation=90, verticalalignment='bottom', color=event_colors[label])
            except TypeError:
                pass

    plt.gca().invert_yaxis() # Flip y-axis upside down as specified by Tim

    plt.xlabel("Time (s)")
    plt.ylabel("MSAS")
    plt.title("MSAS vs Time")
    plt.grid()

    plt.show()

def graph_quality_with_event_markers_single_date(date):
    """
    Graphs data for a single day with important sun and moon events overlaid on the graph.

    Args:
        date (datetime.date() object): The date on which the night to be graphed begins.
    """
    plt.figure()

    sunset, sunrise, all_data = get_all_data(date)

    times, vals = parse.get_values_by_night(parse.time_local, parse.msas, sunset, sunrise)
    plt.plot(times, vals) # Plot time on x-axis, MSAS on y-axis

    for label, time in (all_data).items():
        plt.axvline(x=time, color=event_colors[label])
        plt.text(time, (plt.ylim()[0] + plt.ylim()[1])/2, label.capitalize(), rotation=90, verticalalignment='bottom', color=event_colors[label])

    plt.text(0.5, 0.9, f'Moon Illumination: {weather.moon_illumination(date):.1f}%', horizontalalignment='center', color='slategray', transform=plt.subplot().transAxes)

    plt.gca().invert_yaxis() # Flip y-axis upside down as specified by Tim

    plt.xlabel("Time (s)")
    plt.ylabel("MSAS")
    plt.title("MSAS vs Time")
    plt.grid()

    plt.show()

def graph_all_weather(date):
    sunset, sunrise, all_data = get_all_data(date)

    fig, axs = plt.subplots(2, 1, sharex=True)

    times, vals = parse.get_values_by_night(parse.time_local, parse.msas, sunset, sunrise)
    axs[0].plot(times, vals) # Plot time on x-axis, MSAS on y-axis

    for label, time in (all_data).items():
        axs[0].axvline(x=time, color=event_colors[label])
        axs[0].text(time, (axs[0].get_ylim()[0] + axs[0].get_ylim()[1])/2, label.capitalize(), rotation=90, verticalalignment='bottom', color=event_colors[label])

    axs[0].text(0.5, 0.9, f'Moon Illumination: {weather.moon_illumination(date):.1f}%', horizontalalignment='center', color='slategray', transform=axs[0].transAxes)
    axs[0].set_ylabel("MSAS")
    axs[0].set_title(f"MSAS vs Time: {date}")
    axs[0].xaxis.set_major_formatter(timeFormat)
    axs[0].set_ylim(7, 22)
    axs[0].invert_yaxis() # Flip y-axis upside down as specified by Tim

    weather_data = weather.weather(parse.location, date)
    weather_times, cloud_data = parse.get_values_by_night(weather_data[0], weather_data[1], sunset - timedelta(minutes=30), sunrise + timedelta(minutes=30))
    axs[1].plot(weather_times, cloud_data, color='tomato')
    axs[1].set_ylabel("Cloud Cover (%)")
    axs[1].set_xlabel("Time")
    axs[1].set_title("Cloud Cover vs Time")
    axs[1].xaxis.set_major_formatter(timeFormat)
    axs[1].set_ylim(0, 105)

    plt.grid()
    plt.show()

def graph_max_quality(filter):
    """
    Creates two graphs in the same window. The top graph shows how the maximum MSAS value reached
    during the night changes as the year progresses. The bottom graph shows how the time at which 
    the MSAS value is reached changes as the year progresses. Works best with a large dataset. 
    """
    if(filter):
        qualities, time, dates = weather.remove_bad_days(parse.max_quality_over_time())
    else:
        qualities, time, dates = parse.max_quality_over_time()

    fig, axs = plt.subplots(2,1)

    axs[0].scatter(dates, qualities)
    axs[0].set_ylabel("Max MSAS")
    axs[0].set_title("Max MSAS by Date")
    axs[0].set_ylim(17.5, 22)
    axs[0].invert_yaxis()

    axs[1].scatter(dates, time) #TODO: Make everything have this lovely format
    axs[1].yaxis.set_major_formatter(timeFormat)
    print(timeFormat.tz)
    axs[1].set_xlabel("Date")
    axs[1].set_ylabel("Time of Max MSAS")
    axs[1].set_title("Time of Max MSAS by Date")

    plt.grid()
    plt.show()

def get_all_data(date):
    # TODO: There might be a more efficient way to do this...
    # All of this crazy code is trying to fix the fact that Astral will return data for a day
    # as defined by midnight to midnight rather than data for the night as defined by dusk to
    # dawn, so we have to get some data for the date on which the night starts and some for the
    # date on which the night ends and handle that data accordingly.

    tomorrow = date + timedelta(days = 1)
    
    sun_data = weather.sun_times(parse.location, date)
    sun_data_tomorrow = weather.sun_times(parse.location, tomorrow)
    moon_data = weather.moon_times(parse.location, date)
    moon_data_tomorrow = weather.moon_times(parse.location, tomorrow)

    all_data = {}
    all_data['dusk'] = sun_data['dusk']
    all_data['sunset'] = sun_data['sunset']
    all_data['dawn'] = sun_data_tomorrow['dawn']
    all_data['sunrise'] = sun_data_tomorrow['sunrise']

    sunrise = all_data['sunrise']
    sunset = all_data['sunset']

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

    return sunset, sunrise, all_data