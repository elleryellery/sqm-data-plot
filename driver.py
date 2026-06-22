from tkinter.filedialog import askopenfilenames
import parse
import graph
import weather
import os
import datetime
import time
import predict

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
        print(f'\rReading: {filename}', end="", flush=True)
        parse.printProgressBar(i, num_files, prefix='Upload progress: ', length=50)
        try:
            parse.parse_file(filename)
        except:
            print(f'Error processing {filename}')
    
    print(f'Finished uploading all files in {(time.perf_counter() - start_time):.2f}s. Number of duplicates: {parse.num_duplicates}')

    parse.time_utc, parse.time_local, parse.temp, parse.count, parse.freq, parse.msas = parse.sort_all()

    graph.timeFormat = graph.update_time_format()
    weather.update_big_weather()

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
    print('  7. Create predicted values for a date.')
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
                graph.graph_all_weather(date)

        case '4':
            input_date = input('Please input a date in the format YYYY/MM/DD: ')
            year, day, month = input_date.split('/')
            date = datetime.date(int(year), int(day), int(month))
            weather.bad_day(parse.location, date, verbose=True)
            graph.graph_all_weather(date)

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

# Use the below code to test features with a text input menu. Or, comment it out and
# add your own code to test.

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

read_file()

while(True):
    menu_prompt()
    clear_terminal()

#for date in parse.find_nomoon_nocloud():
    #graph.graph('date-with-fit', date=date)

#predict.get_moon_factor()

#predict.get_cloud_factor(0)

#graph.test_fit()
#msas, times, dates = parse.max_quality_over_time()
#weather.no_moon(msas[0:], times[0:], dates[0:])