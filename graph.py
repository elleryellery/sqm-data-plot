import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import parse

def graph_quality():
    """
    Graphs the quality over time for the entire dataset.
    """
    plt.figure()
    plt.plot(parse.format(parse.time_local), parse.msas) # Plot time on x-axis, MSAS on y-axis

    plt.gca().invert_yaxis() # Flip y-axis upside down as specified by Tim

    plt.xlabel("Time (s)")
    plt.ylabel("MSAS")
    plt.title("MSAS vs Time")
    plt.grid()

    plt.show()

def graph_max_quality():
    """
    Creates two graphs in the same window. The top graph shows how the maximum MSAS value reached
    during the night changes as the year progresses. The bottom graph shows how the time at which 
    the MSAS value is reached changes as the year progresses. Works best with a large dataset. 
    """
    qualities, time, dates = parse.max_quality_over_time()

    fig, axs = plt.subplots(2,1)

    axs[0].plot(dates, qualities)
    axs[0].set_ylabel("Max MSAS")
    axs[0].set_title("Max MSAS by Date")

    axs[1].plot(dates, time) #TODO: This graph has a bug
    timeFormat = mdates.DateFormatter('%H:%M')
    axs[1].yaxis.set_major_formatter(timeFormat)
    axs[1].set_xlabel("Date")
    axs[1].set_ylabel("Time of Max MSAS")
    axs[1].set_title("Time of Max MSAS by Date")

    plt.grid()
    plt.show()