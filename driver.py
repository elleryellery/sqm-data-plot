from tkinter.filedialog import askopenfilenames
import parse
import graph
import weather
import datetime
from datetime import timedelta
import time

def read_file():
    filenames = askopenfilenames(filetypes=[("DAT File", "*.dat")])
    num_files = len(filenames)

    start_time = time.perf_counter()

    for i in range(num_files):
        filename = filenames[i]
        parse.printProgressBar(i, num_files, prefix='Upload progress: ', length=50)
        try:
            parse.parse_file(filename)
        except:
            print(f'WARNING: Error occurred in processing \'{filename}\'.')
    
    print(f'Finished uploading all files in {(time.perf_counter() - start_time):.2f}s. Skipped {parse.num_duplicates} duplicate data points.')

    parse.sort_all()
    graph.timeFormat = graph.update_time_format()
    weather.update_all_weather()

################################################################################################
###################################### TERMINAL PROMPTING ######################################
################################################################################################

def filter_prompt():
    """
    Returns the user-specified data filter style. Defaults to no filter if user input is not
    recognized.

    Returns:
        str: the specified filter style ('by dawn/dusk', 'by value', or 'none')
    """
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
        
def date_prompt():
    """
    Returns a user-specified date.

    Returns:
        datetime.date: specified date
    """
    input_date = input('Please input a date in the format YYYY/MM/DD: ')
    year, day, month = input_date.split('/')
    return datetime.date(int(year), int(day), int(month))

def date_prompt_string():
    input_date = input('Please input a date in the format YYYY/MM/DD: ')
    return input_date

def menu_prompt():
    """
    Gives the full menu of features to view or test. Returns nothing and runs commands for
    each feature within the match case.
    """
    print('Available features:')
    print('  1. Graph quality over all nights.')
    print('  2. Graph quality with sunrise/sunset/moonrise/moonset markers over all nights.')
    print('  3. Graph quality with markers and weather for all individual nights.')
    print('  4. Graph quality with markers and weather for a specified night.')
    print('  5. Graph maximum quality over all nights.')
    print('  6. View annual sinusoidal effect fit curve.')
    print('  7. Test prediction model on a date in the past.')
    print('  8. Predict data for a date in the future.')
    print('  9. Generate predictions for this week.')
    print('  10. Add another file to the dataset.')
    print('  11. Open command line.')

    feature = input('Select a feature: ')

    match feature:
        case '1': # Graph quality over all nights
            filter = filter_prompt()
            cmd = f'raw-all%filter={filter}&invert'
            graph.graph(cmd)
        
        case '2': # Graph quality with markers over all nights.
            filter = filter_prompt()
            cmd = f'raw-all%filter={filter} OVERLAY markers-all&invert'
            graph.graph(cmd)
        
        case '3': # Graph quality with markers for all individual nights.
            for date in parse.get_unique_dates(parse.time_local)[:-1]:
                date = str(date.year) + '/' + str(date.month) + '/' + str(date.day)
                cmd = f'raw-individual%date={date} OVERLAY markers-individual%date={date}&invert SPLIT weather%date={date}&grid'
                graph.graph(cmd)

        case '4': # Graph quality with markers for a specified night.
            date = date_prompt_string()
            cmd = f'raw-individual%date={date} OVERLAY markers-individual%date={date}&invert SPLIT weather%date={date}&grid'
            graph.graph(cmd)

        case '5': # Graph maximum quality over all nights
            filter = input('Filter datapoints to remove nights affected by moonlight? (Y/N)') == 'Y'
            cmd = f'sinusoidal%filter={filter}&invert&grid'
            graph.graph(cmd)

        case '6': # View annual sinusoidal effect fit curve.
            cmd = f'sinusoidal%filter=False%color=red OVERLAY sinusoidal%filter=True%color=blue OVERLAY sinfit%color=green&invert&grid'
            graph.graph(cmd)

        case '7': # Test prediction model on a date in the past.
            date = date_prompt_string()
            cmd = f'raw-individual%date={date} OVERLAY markers-individual%date={date} OVERLAY prediction%date={date}%consider_clouds=False%color=purple OVERLAY prediction%date={date}%consider_clouds=False%consider_moon=False%color=gray OVERLAY prediction%date={date}%color=orange&invert&sharex SPLIT weather%date={date}'
            graph.graph(cmd)
        
        case '8': # Use prediction model to get data for a date in the future
            date = date_prompt_string()
            cmd = f'prediction%date={date}%color=green OVERLAY markers-individual%date={date}&invert&sharex SPLIT weather%date={date}'
            graph.graph(cmd)

        case '9': # Use prediction model to generate data for this week
            date = parse.date_to_string(datetime.date.today())
            cmd = f"prediction%date=DATE%color=green OVERLAY markers-individual%date=DATE&invert&sharex#repeat=7#start={date}#mode=o SPLIT weather%date=DATE#repeat=7#start={date}#mode=o"
            graph.graph(cmd)

        case '10': # Add another file to the dataset.
            read_file()

        case '11':
            cmd = input('Input command: ')
            graph.graph(cmd)
         
        case _:
            print('Unknown feature.')
            

################################################################################################
############################################# DRIVER ###########################################
################################################################################################

# Use the below code to test features with a text input menu. Or, comment it out and
# add your own code to test specific features.

read_file() # Do not remove this line unless you know what you're doing!

while(True): # Runs the regular terminal user interface
    menu_prompt()
    parse.clear_terminal()