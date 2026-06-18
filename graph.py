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