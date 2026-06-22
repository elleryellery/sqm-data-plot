import scipy
from scipy.optimize import curve_fit
from scipy import stats
import math
import parse
import datetime
from datetime import timedelta
import numpy as np
import weather
import graph
import matplotlib.pyplot as plt

prediction_timestep = 120

def sinusoid(x, a, b, c, d):
    return a*(np.sin(b*x + c)) + d

def line(x, m, b):
    return m*x + b

def e(x, a, b, c, d):
    return a*np.exp(b*x + c) + d

def baseline_by_average():
    qualities, times, dates = parse.max_quality_over_time()
    return sum(qualities) / len(qualities) # Return average max MSAS value over all date points

def get_baseline_curve():
    unfiltered_qualities, unfiltered_times, unfiltered_dates = parse.max_quality_over_time()
    dates, msas = weather.filter_no_moon(unfiltered_qualities, unfiltered_times, unfiltered_dates)

    dates = [datetime.datetime(t.year, t.month, t.day, 0, 0, 0).timestamp() for t in dates]
    t0 = dates[0]
    x = np.array(dates) - t0

    p0 = [
        0.5,
        2*np.pi/(365.25*86400),
        0,
        np.mean(msas)
    ]
    popt, pcov = curve_fit(sinusoid, x, msas, p0=p0)

    return popt, t0

def get_baseline_graph_data():
    params, t0 = get_baseline_curve()
    a, b, c, d = params

    start = parse.time_local[0].timestamp()
    end = parse.time_local[-1].timestamp()

    times = np.linspace(start, end, 86400)
    vals = sinusoid(times - t0, a, b, c, d)

    times = [datetime.datetime.fromtimestamp(t) for t in times]

    return times, vals

def get_baseline_by_date(date):
    params, t0 = get_baseline_curve()
    a, b, c, d = params
    x = datetime.datetime(date.year, date.month, date.day, 0, 0, 0).timestamp()
    return sinusoid(x, a, b, c, d) - baseline_by_average()

def get_moon_factor(illumination_point):
    references = weather.find_moon_references(parse.msas, parse.get_unique_dates(parse.time_local))
    #references = parse.get_unique_dates(parse.time_local)
    illumination, deltas = [], []
    for reference in references:
        times, vals = parse.get_values_by_night(parse.time_local, parse.msas, reference)
        sunset, sunrise, all_data = graph.get_all_data(reference)
        moonrise = all_data['moonrise']

        before_moon = parse.get_values_by_time(times, vals, moonrise - timedelta(hours=1), moonrise)[1]
        after_moon = parse.get_values_by_time(times, vals, moonrise, moonrise + timedelta(hours=2))[1]
        
        if(len(before_moon) == 0):
            continue

        pre_avg = sum(before_moon) / len(before_moon)
        post_avg = sum(after_moon) / len(after_moon)
        delta = post_avg - pre_avg

        #print(f'Before: {pre_avg} -> After: {post_avg} (Delta = {delta})')
        #graph.graph_all_weather(reference)

        illum = weather.moon_illumination(reference)

        if(delta < 0.0 and not(illum < 50.0 and delta < -0.25)):
            deltas.append(delta)
            illumination.append(illum)

    illumination, deltas = zip(*sorted(zip(illumination, deltas)))

    p0 = [
        -1,
        0.038,
        -4.6,
        0
    ]

    #params, _ = curve_fit(e, illumination, deltas, p0=p0)
    params = p0
    a, b, c, d = params

    #print(params)

    #x = np.linspace(0, 100, 5)
    #y = e(x, a, b, c, d)

    #plt.figure()
    #plt.scatter(illumination, deltas)
    #plt.plot(x, y, color='green')
    #plt.grid()
    #plt.show()
    
    return e(illumination_point, a, b, c, d)

def get_cloud_factor(cloud_cover):
    dates = parse.get_unique_dates(parse.time_local)
    times_filtered, vals_filtered = weather.filter_no_moon(parse.time_local, parse.msas, dates)
    cloud_points = []
    msas_points = []
    for i in range(len(dates)):
        #parse.printProgressBar(i, len(dates), "Processing cloud cover relation: ", length=50)
        date = dates[i]

        times, msas = times_filtered, vals_filtered#parse.get_values_by_night(times_filtered, vals_filtered, date)

        print(times)
        print(msas)

        weather_times, clouds = weather.from_big_weather_night(date)

        for j in range(len(times)):
            time = times[j]
            if time.minute == 0:
                time = datetime.datetime(time.year, time.month, time.day, time.hour, 0, 0, tzinfo=parse.location.timezone)
                cloud_points.append(clouds[weather_times.index(time)])
                msas_points.append(msas[j])
        

    plt.figure()
    plt.scatter(cloud_points, msas_points)
    plt.grid()
    plt.show()

def make_prediction(date, consider_date=True, consider_moon=True, consider_clouds=True):
    print('Finding solar parameters...')
    times, predictions = predict_sky_model(date)

    if(consider_date): 
        print('Considering sinusoidal effect...') 
        delta = get_baseline_by_date(date) 
        predictions = [p + delta for p in predictions]

    if(consider_moon):
        print('Considering moon effects...')
        illumination = weather.moon_illumination(date)
        moon_factor = get_moon_factor(illumination)
    else:
        moon_factor = 0
    
    sunset, sunrise, all_data = graph.get_all_data(date)

    sunset_num = sunset.timestamp()

    try:
        moonrise_num = all_data['moonrise'].timestamp()
    except: # To handle for no moonrise
        moonrise_num = 0

    try:
        moonset_num = all_data['moonset'].timestamp()
    except: # To handle for no moonset
        moonset_num = 0

    print('Updating predictions...')
    for i in range(len(times)):
        time = times[i] + sunset_num
        if(moonrise_num < time and (moonset_num > time or moonset_num == 0)):
            predictions[i] = predictions[i] - 0.0046*math.sqrt(-moon_factor*5.94*(time-moonrise_num))

    times = [datetime.datetime.fromtimestamp(t + sunset_num).replace(tzinfo=parse.location.timezone) for t in times]
    predictions = [float(p) for p in predictions]

    print('Done!')
    return times, predictions         

def sigmoid(x, x0, k): ##FROM CHAT GPT!! WHAT IS A SIGMOID!!!
    return 1/(1 + np.exp(-k*(x-x0)))

def sky_model(x, baseline, amp_dusk, t_dusk, k_dusk, amp_dawn, t_dawn, k_dawn): ## FROM CHAT GPT!!!

    return (
        baseline
        - amp_dusk * sigmoid(x, t_dusk, k_dusk)
        + amp_dawn * sigmoid(x, t_dawn, k_dawn)
    )

def sky_fit(date):
    times, vals = parse.get_values_by_night(parse.time_local, parse.msas, date)
    _, _, all_data = graph.get_all_data(date)

    t0 = times[0].timestamp()
    times = [t.timestamp() - t0 for t in times]

    p0 = [ ##VALUES FROM CHAT GPT!! SORRY!! I DON"T KNOW WHAT A SIGMOID IS!!
        get_baseline_by_date(date),
        12.0,      # dusk amplitude
        all_data['dusk'].timestamp() - t0,      # dusk time
        1/3600.0,       # dusk steepness
        12.0,      # dawn amplitude
        all_data['dawn'].timestamp() - t0,       # dawn time
        1/3600.0        # dawn steepness
    ]

    params, _ = curve_fit(sky_model, times, vals, p0=p0)

    return params

def predict_sky_fit_params(date):
    times, _ = parse.get_values_by_night(parse.time_local, parse.msas, date)
    _, _, all_data = graph.get_all_data(date)

    t0 = times[0].timestamp()
    dusk = all_data['dusk'].timestamp() - t0
    dawn = all_data['dawn'].timestamp() - t0

    all_params = []

    for date in parse.find_nomoon_nocloud():
        all_params.append(sky_fit(date))

    param_array = np.array(all_params)
    param_predictions = []

    num_nights = param_array.shape[0]

    param_predictions.append(sum(param_array[:,0]) / num_nights)
    param_predictions.append(sum(param_array[:,1]) / num_nights)
    param_predictions.append(dusk)
    param_predictions.append(sum(param_array[:,3]) / num_nights)
    param_predictions.append(sum(param_array[:,4]) / num_nights)
    param_predictions.append(dawn)
    param_predictions.append(sum(param_array[:,6]) / num_nights)

    return param_predictions

def predict_sky_model(date):
    baseline, amp_dusk, t_dusk, k_dusk, amp_dawn, t_dawn, k_dawn = predict_sky_fit_params(date)

    sunset, sunrise, _ = graph.get_all_data(date)

    t0 = sunset.timestamp()

    times = np.linspace(0, sunrise.timestamp() - t0, prediction_timestep)

    print('Creating baseline model...')
    vals = sky_model(times, baseline, amp_dusk, t_dusk, k_dusk, amp_dawn, t_dawn, k_dawn)

    return times, vals

def graph_sky_model(date):
    sunset, sunrise, _ = graph.get_all_data(date)

    t0 = sunset.timestamp()

    times = np.linspace(0, sunrise.timestamp() - t0, prediction_timestep)

    baseline, amp_dusk, t_dusk, k_dusk, amp_dawn, t_dawn, k_dawn = sky_fit(date)

    vals = sky_model(times, baseline, amp_dusk, t_dusk, k_dusk, amp_dawn, t_dawn, k_dawn)

    times = [datetime.datetime.fromtimestamp(t + t0).replace(tzinfo=parse.location.timezone) for t in times]

    return times, vals
