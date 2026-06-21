from tkinter.filedialog import askopenfilenames
import parse
import graph
import weather
import os
import datetime
import time

# I changed this file so that it can do a nice little menu in the terminal that responds to 
# user prompts. If you want to add features to the menu, be sure to update the menu_prompt()
# method. If you want to remove the menu prompt feature to test out code manually, scroll to the
# bottom of the file.

def read_file():
    filenames = askopenfilenames(filetypes=[("DAT File", "*.dat")])
    num_files = len(filenames)

    start_time = time.perf_counter()

    for i in range(num_files):
        filename = filenames[i]
        clear_terminal()
        print(f'Reading: {filename}')
        printProgressBar(i, num_files, prefix='Upload progress: ', length=50)
        try:
            parse.parse_file(filename)
        except:
            print(f'Error processing {filename}')
    
    clear_terminal()
    print(f'Finished uploading all files in {(time.perf_counter() - start_time):.2f}s. Number of duplicates: {parse.num_duplicates}\n')

    parse.time_utc, parse.time_local, parse.temp, parse.count, parse.freq, parse.msas = parse.sort_all()

def filter_prompt():
    print('Available data filter styles:')
    print('   1. Only include values not between dusk and dawn.')
    print('   2. Only include values greater than a certain number.')
    print('   3. Include all values.')

    filter = input('Select a filter type: ')

    match filter:
        case '1':
            return 'by dawn/dusk'
        case '2':
            graph.msas_night_threshold = float(input('Enter a threshold value: '))
            return 'by value'
        case '3':
            return 'none'
        case _:
            print('Unknown filter value. Defaulting to none.')
            return 'none'

def menu_prompt():
    print('Available features:')
    print('  1. Graph quality over all nights.')
    print('  2. Graph quality with sunrise/sunset/moonrise/moonset markers over all nights.')
    print('  3. Graph quality with markers for all individual nights.')
    print('  4. Graph quality with markers for a specified night.')
    print('  5. Graph maximum quality over all nights.')
    print('  6. Add another file to the dataset.')

    feature = input('Select a feature: ')

    match feature:
        case '1':
            graph.graph_quality(filter_prompt())
        
        case '2':
            graph.graph_quality_with_event_markers(filter_prompt())
        
        case '3':
            for date in parse.get_unique_dates()[:-1]:
                graph.graph_quality_with_event_markers_single_date(date)

        case '4':
            input_date = input('Please input a date in the format YYYY/MM/DD: ')
            year, day, month = input_date.split('/')
            graph.graph_quality_with_event_markers_single_date(datetime.date(int(year), int(day), int(month)))

        case '5':
            graph.graph_max_quality()

        case '6':
            read_file()
                
        case _:
            print('Unknown feature.')

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    
    CREDIT TO SOME GUY ON STACK OVERFLOW: https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
    
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

# Use the below code to test features with a text input menu. Or, comment it out and
# add your own code to test.

read_file()

while(True):
    menu_prompt()
    clear_terminal()