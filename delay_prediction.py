
from numpy import NaN
import psycopg2
import pandas as pd
from datetime import datetime, timedelta, date
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn import metrics
from math import sin, sqrt
import numpy as np
import matplotlib.pyplot as plt
import json
import urllib.request
import urllib.error
import ssl


# Connect to the database
# The database create table is in a text file called database, just copy and run it in pgadmin
# Need to create a database in pgadmin first and change these parameters into your own details to allow succesful connection
conn = psycopg2.connect(database = 'train', user = 'postgres', password='meow',host='127.0.0.1', port='5432')
# Create a cursor
cursor = conn.cursor()
# Execute the command
cursor.execute('SELECT * FROM trainperformance')
# Get all the row in traindata
data = cursor.fetchall()

df = pd.DataFrame(data, columns=['rid', 'tpl', 'pta', 'ptd', 'wta', 'wtp', 'wtd', 'arr_et', 'arr_wet', 'arr_atRemoved',	'pass_et', 'pass_wet', 'pass_atRemoved', 'dep_et', 'dep_wet', 'dep_atRemoved', 'arr_at', 'pass_at', 'dep_at', 'cr_code', 'lr_code'])
# Close connection
df['rid'] = df['rid'].astype('str')
conn.close()

weymouth_weather_df = pd.read_csv('weymouth_weathers.csv')

single_performance_df = pd.read_csv('single_train_performance.csv')

time_difference = {'From':[], 'To':[], 'Minutes':[]}

def estimate_time_difference():
    for i in range(0, 61):
        departing_station = single_performance_df.loc[i]['tpl']
        arriving_station = single_performance_df.loc[i + 1]['tpl']
        departing_time = ''
        arriving_time = ''
        if isinstance(single_performance_df.loc[i]['ptd'], str):
            departing_time = single_performance_df.loc[i]['ptd']
        elif isinstance(single_performance_df.loc[i]['wtp'], str):
            departing_time = single_performance_df.loc[i]['wtp']
        else:
            departing_time = single_performance_df.loc[i]['pta']

        if isinstance(single_performance_df.loc[i+1]['pta'], str):
            arriving_time = single_performance_df.loc[i + 1]['pta']
        elif isinstance(single_performance_df.loc[i+1]['wtp'], str):
            arriving_time = single_performance_df.loc[i + 1]['wtp']
        else:
            arriving_time = single_performance_df.loc[i + 1]['ptd']
        print("----------------------------")
        print(arriving_station + " " + departing_station)
        print(departing_time.strip()[:5].zfill(5) + " " + arriving_time.strip()[:5].zfill(5))
        time_minutes = (datetime.strptime(arriving_time.strip().zfill(5), '%H:%M') - datetime.strptime(departing_time.strip().zfill(5), '%H:%M')).total_seconds()/60 
        print(time_minutes)
        time_difference['From'].append(departing_station)
        time_difference['To'].append(arriving_station)
        time_difference['Minutes'].append(time_minutes)
        
    time_difference_df = pd.DataFrame(time_difference)
    return time_difference_df

def calculate_arrival_time(begin_station, destination_station, left_time_string, delay_amount, time_difference_df, prediction_model):
    left_time_date = datetime.strptime(left_time_string, '%H:%M')

    from_index = time_difference_df.index[time_difference_df['From'] == begin_station].tolist()[0]
    to_index = time_difference_df.index[time_difference_df['To'] == destination_station].tolist()[0]
    print(time_difference_df)
    mins = int(sum(time_difference_df['Minutes'].iloc[from_index:to_index + 1]))

    estimate_time = left_time_date + timedelta(minutes=mins + delay_amount)

    ssl._create_default_https_context = ssl._create_unverified_context
    response = urllib.request.urlopen('https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/weymouth/today?unitGroup=metric&key=LDM4JXNEB4J6RUS6N28ZDAWLM&contentType=json')
    data = response.read()
    weatherData = json.loads(data.decode('utf-8'))
    current_temp = weatherData['days'][0]['temp']
    current_precip = weatherData['days'][0]['precip']
    current_condition = icon_to_number(weatherData['days'][0]['icon'])
    current_weekday = is_weekend(date.today().weekday())

    predicted_delay = 0

    for i in range(from_index, to_index + 1):
        left_time_date = left_time_date + timedelta(minutes=time_difference_df.loc[i]['Minutes'])
        current_offtime = is_off_time(str(left_time_date.time()))
        scaled = scaler.transform([[current_temp, current_precip, current_condition, current_offtime, current_weekday]])
        print(int(prediction_model.predict(scaled)))
        predicted_delay = prediction_model.predict(scaled)
    
    estimate_time = estimate_time + timedelta(minutes=int(predicted_delay[0])) 
    print(estimate_time)

def is_off_time(time):
    time = time.strip().zfill(5)
    if ((time > '09:30') and (time < '16:00')) or time > '19:00':
        return True
    else:
        return False

def get_time(row):
    for column in row:
        if isinstance(column, str) and (len(column) == 5 or len(column) == 4):
            return is_off_time(column)



def off_peak_times():
    df['offpeak'] = df.apply(lambda row: get_time(row), axis=1)

def check_autumn(number):
    if  number == '09' or number == '10' or number == '11':
        return 1 #Autumn
    else:
        return 2 #Other

def seasons():
    df['is_autumn'] = df.apply(lambda row : check_autumn(row['rid'][slice(4,6)]), axis=1)

def day_of_week():
    df['isweekend'] = df.apply(lambda row : is_weekend(datetime.strptime(row['rid'][slice(0,8)], '%Y%m%d').weekday()), axis=1)

def is_weekend(day):
    if day > 4:
        return 1
    else:
        return 0

"""
def associated_train_deviation():

    initial_train_date = datetime(2025,9,1)
    first_train = True
    prev_train_id = '734960'

    prev_train_deviations = {}
    curr_train_deviations = {}

    for i in range(0, len(df)):
        print(i)
        train_date = datetime.strptime(df.loc[i]['rid'][slice(0,8)], '%Y%m%d')
        train_id = df.loc[i]['rid'][slice(9,15)]

        if initial_train_date != train_date:
            first_train = True
        elif first_train == True and prev_train_id != train_id:
            first_train = False

        if prev_train_id != train_id:
            prev_train_deviations = curr_train_deviations.copy()
            curr_train_deviations = {}

        if df.loc[i]['dep_at'] != None and df.loc[i]['ptd'] != None:
            train_dev = df.loc[i, 'prev train deviation'] = (datetime.strptime((df.loc[i]['dep_at']).strip(), '%H:%M') - datetime.strptime((df.loc[i]['ptd']).strip(), '%H:%M')).total_seconds()/60
        else:
            train_dev = 0
        curr_train_deviations.update({df.loc[i]['tpl']: train_dev})
        if(df.loc[i]['tpl'] not in prev_train_deviations):
            prev_train_deviations.update({df.loc[i]['tpl']: 0})
        if first_train == False and prev_train_deviations[df.loc[i]['tpl']] != None:
            df.loc[i, 'prev train deviation'] = prev_train_deviations[df.loc[i]['tpl']]
        else:
            df.loc[i, 'prev train deviation'] = 0
        initial_train_date = train_date
        prev_train_id = train_id
"""
def weather():
    df['temperature'] = df.apply(lambda row : get_temperature(datetime.strptime(row['rid'][slice(0,8)], '%Y%m%d').strftime('%Y-%m-%d')), axis=1)
    df['precipitation'] = df.apply(lambda row : get_precipitation(datetime.strptime(row['rid'][slice(0,8)], '%Y%m%d').strftime('%Y-%m-%d')), axis=1)
    df['condition'] = df.apply(lambda row : get_icon(datetime.strptime(row['rid'][slice(0,8)], '%Y%m%d').strftime('%Y-%m-%d')), axis=1)
    df['snowdepth'] = df.apply(lambda row : get_snow(datetime.strptime(row['rid'][slice(0,8)], '%Y%m%d').strftime('%Y-%m-%d')), axis=1)

def get_temperature(date):
    date_temperature_df = weymouth_weather_df[weymouth_weather_df['datetime'] == date]
    return date_temperature_df.values[0][4]

def get_precipitation(date):
    date_precip_df = weymouth_weather_df[weymouth_weather_df['datetime'] == date]
    return date_precip_df.values[0][10]

def icon_to_number(icon):
    if icon == 'snow':
        return 1
    elif icon == 'rain':
        return 2
    elif icon == 'fog':
        return 3
    elif icon == 'wind':
        return 4
    elif icon == 'cloudy':
        return 5
    elif icon == 'partly-cloudy-day':
        return 6
    elif icon == 'partly-cloudy-night':
        return 7
    elif icon == 'clear-day':
        return 8
    elif icon == 'clear-night':
        return 9

def get_icon(date):
    date_icon_df = weymouth_weather_df[weymouth_weather_df['datetime'] == date]
    icon = date_icon_df.values[0][31]
    return icon_to_number(icon)

def get_snow(date):
    date_snow_df = weymouth_weather_df[weymouth_weather_df['datetime'] == date]
    snowdepth = date_snow_df.values[0][15] 
    if isinstance(snowdepth, int):
        return snowdepth
    else:
        return 0

    # 20 -> 15
def mlpregressor(x_train, y_train, x_test, y_test):
    mlp = MLPRegressor(hidden_layer_sizes=15, solver='sgd', max_iter=10000, activation='identity', random_state=0, learning_rate_init=0.001, verbose='True', momentum=0.9, tol=0.0001, early_stopping=False)
    mlp.fit(x_train, y_train)

    y_guess = mlp.predict(x_test)

    print(sqrt(mean_squared_error(y_test, y_guess)), r2_score(y_test, y_guess))

    return mlp

def knn(x_train, y_train, x_test, y_test):
    knn = KNeighborsRegressor(n_neighbors=7)
    knn.fit(x_train, y_train)
    
    neighbors = np.arange(1,9)
    train_accuracy = np.empty(len(neighbors))
    test_accuracy = np.empty(len(neighbors))
    for i, k in enumerate(neighbors):
        knn = KNeighborsRegressor(n_neighbors=k)
        knn.fit(x_train, y_train)

        train_accuracy[i] = knn.score(x_train, y_train)
        test_accuracy[i] = knn.score(x_test, y_test)

    plt.plot(neighbors, test_accuracy, label = 'Testing dataset accuracy')
    plt.plot(neighbors, train_accuracy, label = 'Training dataset accuracy')

    plt.legend()
    plt.xlabel('n_neighbours')
    plt.ylabel('accuracy')
    plt.show()
    return knn

def svregression(x_train, y_train, x_test, y_test):
    svr = SVR()
    svr.fit(x_train, y_train)
    y_guess = svr.predict(x_test)
    print(sqrt(mean_squared_error(y_test, y_guess)), r2_score(y_test, y_guess))
    return svr

#def sgdregression(x_train, y_train, x_test, y_test):



if __name__ == '__main__':
    
    weather()

    off_peak_times()
    seasons()
    day_of_week()

    
    df['arrival_diff'] = df.apply(lambda row : (datetime.strptime((row['arr_at']).strip(), '%H:%M') - datetime.strptime((row['pta']).strip(), '%H:%M')).total_seconds()/60  if row['arr_at'] != None and row['pta'] != None else None, axis=1)
    print(df.info())

    filtered_df = df[df['arr_at'].notnull() & df['pta'].notnull()]
    print(filtered_df.iloc[:,28])

    Y = filtered_df.iloc[:,28]

    X = filtered_df.iloc[:,[21,22,23,24,25,26,27]]
    print(X)
    scaler = StandardScaler()
    scaler.fit(X)

    Xtrain, Xtest, Ytrain, Ytest = train_test_split(X,Y, test_size=0.4, random_state=1)

    Xtrain = scaler.transform(Xtrain)
    Xtest = scaler.transform(Xtest)

    prediction_model = svregression(Xtrain, Ytrain, Xtest, Ytest)
    """
    a = estimate_time_difference()
    calculate_arrival_time('WDON', 'VAUXHLM', '8:00', 10, a, prediction_model)
    """
    
