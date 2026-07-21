import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.transforms import blended_transform_factory
import parse
import weather
from datetime import timedelta
from zoneinfo import ZoneInfo
import predict
from ast import literal_eval

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
    """
    Updates the time formatting after the location has been initialized.
    """
    return mdates.DateFormatter('%H:%M', tz=parse.location.timezone)

def graph_quality_all(filter_type, ax=None, color=None):
    """
    Graphs the quality over time (i.e. throughout the night) for the entire dataset.

    Args:
        filter_type (str): If you wish to remove daytime values from the graph, you must specify
            a filter type. Options are as follows:
                by value: Removes datapoints where the MSAS is below the msas_night_threshold
                by dawn/dusk: Removes datapoints that are not between dawn and dusk
                none: Keeps all values, including daytime ones.
        ax (matplotlib.Axes): axes can be specified to overlay the graph on an existing axes. If not specified, axes will be created.
        color: what color to make the graph
    """
    if(ax==None):
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    if(filter_type == 'by value'):
        x, y = parse.values_by_threshold(msas_night_threshold)
    elif(filter_type == 'by dawn/dusk'):
        x, y = parse.values_dusk_to_dawn(parse.time_local, parse.msas)
    elif(filter_type == 'none'):
        x, y = parse.time_local, parse.msas
    else:
        raise TypeError('Unrecognized filter type.')

    ax.plot(x, y, color=color)

    ax.set_ylim(7, 22)

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("MSAS")
    ax.set_title("MSAS vs Time")
    
    return fig, ax

def graph_markers_all(ax=None):
    """
    Graphs markers showing important sun and moon events for the entire dataset (i.e. dawn, dusk,
    sunrise, sunset, moonrise, moonset, etc.).

    Args:
        ax (matplotlib.Axes): axes can be specified to overlay the graph on an existing axes. If not specified, axes will be created.
    """
    if(ax==None):
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    for date in parse.get_unique_dates(parse.time_local):
        sun_data = weather.sun_times(parse.location, date)
        moon_data = weather.moon_times(parse.location, date)

        for label, time in (sun_data | moon_data).items():
            try:
                ymin, ymax = ax.get_ylim()
                ax.vlines(time, ymin, ymax, color=event_colors[label])
                ax.text(time, (ymin + ymax)/2, label.capitalize(), rotation=90, verticalalignment='bottom', color=event_colors[label])
            except TypeError:
                pass

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("MSAS")
    ax.set_title("MSAS vs Time")

    return fig, ax

def graph_quality_individual(date, ax=None, color=None):
    if(ax==None):
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    ax.set_ylim(7, 22)

    times, vals = parse.get_values_by_night(parse.time_local, parse.msas, date)
    ax.plot(times, vals, color=color) # Plot time on x-axis, MSAS on y-axis

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("MSAS")
    ax.set_title(f"MSAS vs Time: {date}")
    ax.xaxis.set_major_formatter(timeFormat)

    return fig, ax


def graph_markers_individual(date, ax=None):
    """
    Graphs important sun and moon events as vertical line markers. Also labels the graph with the moon illumination
    and date.

    Args:
        date (datetime.date() object): The date on which the night to be graphed begins.
        ax (matplotlib.Axes): axes can be specified to overlay the graph on an existing axes. If not specified, axes will be created.
    """

    if(ax==None):
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    ax.set_ylim(7, 22)

    all_data = weather.get_all_data(date)

    ymin, ymax = ax.get_ylim()

    for label, time in (all_data).items():
        ax.vlines(time, ymin, ymax, color=event_colors[label])
        ax.text(time, (ymin + ymax)/2, label.capitalize(), rotation=90, verticalalignment='bottom', color=event_colors[label])
    
    ax.text(all_data['sunset'] + (all_data['sunrise'] - all_data['sunset'])/2, 0.95, date, horizontalalignment='center', color='black', transform=blended_transform_factory(ax.transData, ax.transAxes))
    ax.text(all_data['sunset'] + (all_data['sunrise'] - all_data['sunset'])/2, 0.9, f'Moon Illumination: {weather.moon_illumination(date):.1f}%', horizontalalignment='center', color='slategray', transform=blended_transform_factory(ax.transData, ax.transAxes))

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("MSAS")

    return fig, ax

def graph_weather(date, ax=None, color='tomato'):
    """
    Graphs the fit curve for the annual sinusoidal effect.

    Args:
        date (datetime.date): date to graph
        ax (matplotlib.Axes): axes can be specified to overlay the graph on an existing axes. If not specified, axes will be created.
        color (str): what color to make the graph
        
    Returns:
        fig, ax: graph objects
    """
    if(ax==None):
        fig, ax = plt.subplots()
    else:
        fig = ax.figure
    
    if(color==None):
        color='tomato'

    weather_times, cloud_data = weather.from_all_weather_night(date)
    if(len(weather_times) == 0):
        weather_times, cloud_data = weather.forecast(date, parse.location)

    ax.plot(weather_times, cloud_data, color=color)
    ax.set_ylabel("Cloud Cover (%)")
    ax.set_xlabel("Time")
    ax.set_title("Cloud Cover vs Time")
    ax.xaxis.set_major_formatter(timeFormat)
    ax.set_ylim(0, 105)

    return fig, ax

def graph_sinusoidal(filter, ax=None, color='blue'):
    """
    Graphs annual sinusoidal effect raw data.

    Args:
        filter (boolean): removes dates with bright moon if enabled
        ax (matplotlib.Axes): axes can be specified to overlay the graph on an existing axes. If not specified, axes will be created.
        color (str): what color to make the graph
        
    Returns:
        fig, ax: graph objects
    """
    if(ax==None):
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    if(filter):
        qualities, time, dates = parse.max_quality_over_time()
        dates, qualities = weather.filter_no_moon(qualities, dates)
    else:
        qualities, time, dates = parse.max_quality_over_time()

    ax.scatter(dates, qualities, color=color)
    ax.set_ylabel("Max MSAS")
    ax.set_title("Max MSAS by Date")
    ax.set_ylim(17.5, 22)

    #axs[1].scatter(dates, time) #TODO: Make everything have this lovely format
    #axs[1].yaxis.set_major_formatter(timeFormat)
    #axs[1].set_xlabel("Date")
    #axs[1].set_ylabel("Time of Max MSAS")
    #axs[1].set_title("Time of Max MSAS by Date")

    return fig, ax

def graph_sinfit(ax=None, color='green'):
    """
    Graphs the fit curve for the annual sinusoidal effect.

    Args:
        ax (matplotlib.Axes): axes can be specified to overlay the graph on an existing axes. If not specified, axes will be created.
        color (str): what color to make the graph
        
    Returns:
        fig, ax: graph objects
    """
    if(ax==None):
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    fit_times, fit_vals = predict.get_baseline_graph_data()
    ax.plot(fit_times, fit_vals, color=color)

    return fig, ax
    
def graph_prediction(date, ax=None, consider_date=True, consider_moon=True, consider_clouds=True, color='green'):
    """
    Graphs the prediction algorithm's output for the specified date.

    Args:
        date (datetime.date): date to graph
        ax (matplotlib.Axes): axes can be specified to overlay the graph on an existing axes. If not specified, axes will be created.
        consider_date (boolean): whether the prediction algorithm should consider annual sinusoidal effects
        consider_moon (boolean): whether the prediction algorithm should consider the effect of the moon
        consider_clouds (boolean): whether the prediction algorithm should consider the effect of clouds
        color (str): the color for the graph to be drawn in

    Returns:
        fig, ax: graph objects
    """
    if(ax==None):
        fig, ax = plt.subplots()
    else:
        fig = ax.figure
        
    times, vals = predict.make_prediction(date, consider_date, consider_moon, consider_clouds)
    ax.plot(times, vals, color=color)
    ax.set_title(f'Predicted MSAS vs. Time: {date}')

    return fig, ax

def graph(command):
    """
    A function to make graphs and overlay graphs on top of each other. Interprets a string command to generate 
    graphs meeting the specified requirements.

    Args:
        command (str): a command formatted according to the rules outlined in the README
    """

    graphs = command.split(' SPLIT ')
    fig, axs = plt.subplots(len(graphs), 1, squeeze=False, constrained_layout=True)

    for i in range(len(graphs)):
        # Interpret repeat commands
        if('#repeat=' in graphs[i]):
            repeat_commands = graphs[i].split('#')
            num_repeats = 1
            start_date = None
            mode = ' SPLIT '
            for cmd in repeat_commands[1:]:
                if('repeat=' in cmd):
                    num_repeats = int(cmd.split('=')[1])
                elif('start=' in cmd):
                    start_date = parse.get_datetimedate(cmd.split('=')[1])
                elif('mode=' in cmd):
                    if(cmd.split('=')[1] == 'o'):
                        mode = ' OVERLAY '

            base_command = graphs[i].split('&')[0].split('#')[0]
            set = graphs[i].split('#')[0].split('&')[1:]

            graphs[i] = ''
            for j in range(num_repeats):
                graphs[i] += base_command.replace('DATE', parse.date_to_string(start_date + timedelta(days=j)))
                if(j < num_repeats - 1):
                    graphs[i] += mode
                else:
                    for s in set:
                        graphs[i] += '&' + s

        settings = graphs[i].split('&')
        data = settings[0].split(' OVERLAY ')
        settings = settings[1:]
        for dat in data:
            # Default qualifier values
            date = None
            filter = None
            color = None
            consider_date = True
            consider_moon = True
            consider_clouds = True

            # Qualifier parsing
            secs = dat.split('%')
            qualifiers = secs[1:]
            dat = secs[0]
            for qualifier in qualifiers:
                if('date' in qualifier):
                    date = parse.get_datetimedate(qualifier.split('=')[1])
                elif('filter' in qualifier):
                    f = qualifier.split('=')[1]
                    try:
                        filter = literal_eval(f) # For boolean filter types
                    except:
                        filter = f # For string filter types
                elif('color' in qualifier):
                    color = qualifier.split('=')[1]
                elif('consider_date' in qualifier):
                    consider_date = qualifier.split('=')[1] == 'True'
                elif('consider_moon' in qualifier):
                    consider_moon = qualifier.split('=')[1] == 'True'
                elif('consider_clouds' in qualifier):
                    consider_clouds = qualifier.split('=')[1] == 'True'

            # Graph command parsing
            ax = axs[i][0]
            ax.grid(True)
            match(dat):
                case 'raw-all': # MSAS vs. time for all dates
                    graph_quality_all(filter, ax, color)
                case 'raw-individual': # MSAS vs. time for a single date
                    graph_quality_individual(date, ax, color)
                case 'markers-all': # Sun/moon event markers for all dates
                    graph_markers_all(ax)
                case 'markers-individual': # Sun/moon event markers for a single date
                    graph_markers_individual(date, ax)
                case 'weather': # Cloud cover data
                    graph_weather(date, ax, color)
                case 'sinusoidal': # Annual sinusoidal effect raw data
                    graph_sinusoidal(filter, ax, color)
                case 'sinfit': # Best fit curve for annual sinusoidal effect data
                    graph_sinfit(ax, color)
                case 'prediction': # Predicted MSAS curve for a date
                    graph_prediction(date, ax, consider_date, consider_moon, consider_clouds, color)
                case _:
                    print(f'ERROR: Unrecognized command: \'{dat}\'')

        # Setting parsing
        for setting in settings:
            if('invert' in setting):
                ax.invert_yaxis()
            elif('grid' in setting):
                ax.grid(True)
            elif('sharex' in setting):
                for a in range(len(axs) - 1, 0, -1):
                    axs[a][0].sharex(axs[a-1][0])


    plt.show()