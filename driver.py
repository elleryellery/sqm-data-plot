from tkinter.filedialog import askopenfilename
import parse
import graph
import weather

filename = askopenfilename(filetypes=[("DAT File", "*.dat")])

parse.parse_file(filename)

# I changed this file so that it can do a nice little menu in the terminal that responds to 
# user prompts. If you want to add features to the menu, be sure to update the menu_prompt()
# method. If you want to remove the menu prompt feature to test out code manually, scroll to the
# bottom of the file.

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
    print('  3. Graph quality with markers for individual nights.')
    print('  4. Graph maximum quality over all nights.')

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
            graph.graph_max_quality()
                
        case _:
            print('Unknown feature.')

# Use the below code to test features with a text input menu. Or, comment it out and
# add your own code to test.

while(True):
    menu_prompt()