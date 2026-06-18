import matplotlib.pyplot as plt
import parse

def graph_quality():
    plt.figure()
    plt.plot(parse.format(parse.time_local), parse.msas) # Plot time on x-axis, MSAS on y-axis

    plt.gca().invert_yaxis() # Flip y-axis upside down as specified by Tim

    plt.xlabel("Time (s)")
    plt.ylabel("MSAS")
    plt.title("MSAS vs Time")
    plt.grid()

    plt.show()

def graph_max_quality():
    qualities, time, dates = parse.max_quality_over_time()

    fig, axs = plt.subplots(2,1)

    axs[0].plot(dates, qualities)
    axs[0].set_xlabel("Date")
    axs[0].set_ylabel("Max MSAS")
    axs[0].set_title("Max MSAS by Date")

    axs[1].plot(dates, time) #TODO: This graph has a bug
    axs[1].set_xlabel("Date")
    axs[1].set_ylabel("Time of Max MSAS")
    axs[1].set_title("Time of Max MSAS by Date")

    plt.grid()
    plt.show()