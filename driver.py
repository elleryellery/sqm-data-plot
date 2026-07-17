from tkinter.filedialog import askopenfilenames
import parse
import graph
import weather
import datetime
import time

def read_file():
    filenames = askopenfilenames(filetypes=[("DAT File", "*.dat")])
    num_files = len(filenames)

    start_time = time.perf_counter()

    for i in range(num_files):
        filename = filenames[i]
        print(f'\rReading: {filename}', end="", flush=True)
        parse.printProgressBar(i, num_files, prefix='Upload progress: ', length=50)
        try:
            parse.parse_file(filename)
        except:
            print(f'Error processing {filename}')
    
    print(f'Finished uploading all files in {(time.perf_counter() - start_time):.2f}s. Number of duplicates: {parse.num_duplicates}')

    parse.sort_all()

    graph.timeFormat = graph.update_time_format()
    weather.update_all_weather()

################################################################################################
###################################### TERMINAL PROMPTING ######################################
################################################################################################

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
    print('  7. Test prediction model on a date in the past.')
    print('  8. Test baseline fit.')

    feature = input('Select a feature: ')

    match feature:
        case '1':
            graph.graph_quality(filter_prompt())
        
        case '2':
            graph.graph_quality_with_event_markers(filter_prompt())
        
        case '3':
            for date in parse.get_unique_dates(parse.time_local)[:-1]:
                #graph.graph_quality_with_event_markers_single_date(date)
                graph.graph('date-with-weather', date=date)

        case '4':
            input_date = input('Please input a date in the format YYYY/MM/DD: ')
            year, day, month = input_date.split('/')
            date = datetime.date(int(year), int(day), int(month))
            weather.bad_day(date)
            graph.graph('date-with-weather', date=date)

        case '5':
            filter = input('Remove datapoints from cloudy days? (Y/N)') == 'Y'
            graph.graph_max_quality(filter)

        case '6':
            read_file()

        case '7':
            input_date = input('Please input a date in the format YYYY/MM/DD: ')
            year, day, month = input_date.split('/')
            date = datetime.date(int(year), int(day), int(month))
            graph.graph('date-with-fit', date=date)
        
        case '8':
            graph.test_fit()
                
        case _:
            print('Unknown feature.')

################################################################################################
############################################# DRIVER ###########################################
################################################################################################

# Use the below code to test features with a text input menu. Or, comment it out and
# add your own code to test specific features.

read_file() # I recommend against removing this line!

while(True): # Runs the regular terminal user interface
    menu_prompt()
    parse.clear_terminal()
