
from numpy import NaN
import psycopg2
import pandas as pd
from datetime import datetime, timedelta, date
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import LinearSVR
from math import sin, sqrt
import numpy as np
import matplotlib.pyplot as plt
import json
import urllib.request
import urllib.error
import ssl
import joblib

# Connect to the database
# The database create table is in a text file called database, just copy and run it in pgadmin
# Need to create a database in pgadmin first and change these parameters into your own details to allow succesful connection
conn = psycopg2.connect(database = 'train', user = 'postgres', password='meow', host='127.0.0.1', port='5432')
#conn = psycopg2.connect(database = 'AIdatabase', user = 'postgres', password='account7248',host='127.0.0.1', port='5432')
# Create a cursor
cursor = conn.cursor()

cursor.execute('SELECT * FROM trainperformance')

data = cursor.fetchmany(320000) # Get all the row in traindata

cursor.execute('SELECT * FROM weather2017')

weatherdata = cursor.fetchall()

cursor.execute('SELECT * FROM singletrainperformance')

singledata = cursor.fetchall()

df = pd.DataFrame(data, columns=['rid', 'tpl', 'pta', 'ptd', 'wta', 'wtp', 'wtd', 'arr_et', 'arr_wet', 'arr_atRemoved',	'pass_et', 'pass_wet', 'pass_atRemoved', 'dep_et', 'dep_wet', 'dep_atRemoved', 'arr_at', 'pass_at', 'dep_at', 'cr_code', 'lr_code'])

cursor.execute('SELECT * FROM station')

stationsdata = cursor.fetchall()

stations = pd.DataFrame(stationsdata, columns=['name', 'longname.name_alias', 'alpha3', 'tiploc', 'abb'])

#stations = pd.read_csv("stations.csv")

weymouth_weather_df = pd.DataFrame(weatherdata, columns=['name', 'datetime', 'tempmax',	'tempmin',	'temp',	'feelslikemax',	'feelslikemin',	'feelslike', 'dew',	'humidity',	'precip', 'precipprob',	'precipcover',	'preciptype', 'snow', 'snowdepth', 'windgust', 'windspeed',	'winddir', 'sealevelpressure', 'cloudcover', 'visibility',	'solarradiation', 'solarenergy', 'uvindex', 'severerisk', 'sunrise', 'sunset', 'moonphase', 'conditions', 'description', 'icon', 'stations'])

# Close connection
df['rid'] = df['rid'].astype('str')

#weymouth_weather_df = pd.read_csv('southampton_weather_2017_days.csv')
cursor.execute('SELECT * FROM singletrainperformance')

singleperformancedata = cursor.fetchall()

conn.close()

single_performance_df = pd.DataFrame(singleperformancedata, columns=['rid', 'tpl', 'pta', 'ptd', 'wta', 'wtp', 'wtd', 'arr_et', 'arr_wet', 'arr_atRemoved',	'pass_et', 'pass_wet', 'pass_atRemoved', 'dep_et', 'dep_wet', 'dep_atRemoved', 'arr_at', 'pass_at', 'dep_at', 'cr_code', 'lr_code'])

#single_performance_df = pd.read_csv('single_train_performance.csv')

time_difference = {'From':[], 'Minutes':[]}

def estimate_time_difference():
    for i in range(0, 61):
        departing_station = single_performance_df.loc[i]['tpl'].strip()
        arriving_station = single_performance_df.loc[i + 1]['tpl'].strip()
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
        arriving_array = stations.loc[stations['abb'] == arriving_station]['tiploc'].values
        departing_array = stations.loc[stations['abb'] == departing_station]['tiploc'].values
        if len(arriving_array) > 0:
            arriving_station = arriving_array[0]
        else:
            arriving_station = ''
        if len(departing_array) > 0:
            departing_station = departing_array[0]
        else:
            departing_station = ''
        print(departing_time.strip()[:5].zfill(5) + " " + arriving_time.strip()[:5].zfill(5))
        time_minutes = (datetime.strptime(arriving_time.strip().zfill(5), '%H:%M') - datetime.strptime(departing_time.strip().zfill(5), '%H:%M')).total_seconds()/60 
        print(time_minutes)
        """
        time_difference['From'].append(departing_station)
        time_difference['To'].append(arriving_station)
        """
        time_difference['From'].append(departing_station)
        time_difference['Minutes'].append(time_minutes)
    time_difference['From'].append('WAT')
    time_difference['Minutes'].append(0)
    time_difference_df = pd.DataFrame(time_difference)
    print(time_difference_df)
    return time_difference_df

def calculate_arrival_time(begin_station, destination_station, left_time_date, delay_amount, time_difference_df, prediction_model, scaler):
    #left_time_date = datetime.strptime(left_time_string, '%H:%M')
    
    from_index = time_difference_df.index[time_difference_df['From'] == begin_station].tolist()[0]
    #to_index = time_difference_df.index[time_difference_df['To'] == destination_station].tolist()[0]
    to_index = time_difference_df.index[time_difference_df['From'] == destination_station].tolist()[0]
    print(time_difference_df)
    print(from_index)
    print(to_index)
    if to_index > from_index:
        mins = int(sum(time_difference_df['Minutes'].iloc[from_index:to_index]))
    else:
        mins = int(sum(time_difference_df['Minutes'].iloc[to_index:from_index]))
        temp_index = from_index
        from_index = to_index
        to_index = temp_index
    print(mins)
    estimate_time = left_time_date + timedelta(minutes=mins) + delay_amount

    ssl._create_default_https_context = ssl._create_unverified_context
    response = urllib.request.urlopen('https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/southampton/today?unitGroup=metric&key=LDM4JXNEB4J6RUS6N28ZDAWLM&contentType=json')
    data = response.read()
    weatherData = json.loads(data.decode('utf-8'))
    current_temp = weatherData['days'][0]['temp']
    current_precip = weatherData['days'][0]['precip']
    current_condition = icon_to_number(weatherData['days'][0]['icon'])
    current_snowdepth = weatherData['days'][0]['snowdepth']
    current_season = check_season(datetime.now().strftime('%m'))
    predicted_delay = 0

    for i in range(from_index, to_index):
        print('---')
        print(time_difference_df.loc[i]['Minutes'])
        left_time_date = left_time_date + timedelta(minutes=time_difference_df.loc[i]['Minutes'])
        print(left_time_date)
        current_offtime = is_off_time(str(left_time_date.time()), date.today().weekday())
        scaled = scaler.transform([[current_temp, current_precip, current_condition, current_snowdepth, current_offtime, current_season]])
        predicted_delay = prediction_model.predict(scaled)
    
    estimate_time = estimate_time + timedelta(minutes=int(predicted_delay[0])) 
    return estimate_time

def is_off_time(time, day):
    time = time.strip().zfill(5)
    if (((time > '09:30') and (time < '16:00')) or time > '19:00') or is_weekend(day):
        return True
    else:
        return False

def get_time(row, day):
    for column in row:
        if isinstance(column, str) and (len(column) == 5 or len(column) == 4):
            return is_off_time(column, day)



def off_peak_times():
    df['offpeak'] = df.apply(lambda row: get_time(row, datetime.strptime(row['rid'][slice(0,8)], '%Y%m%d').weekday()), axis=1)

def check_season(number):
    if  number == '09' or number == '10' or number == '11':
        return 1 #Autumn
    elif number == '12' or number == '01' or number == '02':
        return 2
    elif number == '03' or number == '04' or number == '05':
        return 3
    else:
        return 4

def seasons():
    df['is_season'] = df.apply(lambda row : check_season(row['rid'][slice(4,6)]), axis=1)

def is_weekend(day):
    if day > 4:
        return 1
    else:
        return 0

def weather():
    df['temperature'] = df.apply(lambda row : get_temperature(datetime.strptime(row['rid'][slice(0,8)], '%Y%m%d').strftime('%Y-%m-%d')), axis=1)
    df['precipitation'] = df.apply(lambda row : get_precipitation(datetime.strptime(row['rid'][slice(0,8)], '%Y%m%d').strftime('%Y-%m-%d')), axis=1)
    df['condition'] = df.apply(lambda row : get_icon(datetime.strptime(row['rid'][slice(0,8)], '%Y%m%d').strftime('%Y-%m-%d')), axis=1)
    df['snowdepth'] = df.apply(lambda row : get_snow(datetime.strptime(row['rid'][slice(0,8)], '%Y%m%d').strftime('%Y-%m-%d')), axis=1)

# temperature to check if cold temperature or not
def get_temperature(date):
    date_temperature_df = weymouth_weather_df[weymouth_weather_df['datetime'] == date]
    temperature = date_temperature_df.values[0][4]
    return temperature

# check if rain to if hard rain
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
    
    icon = date_icon_df.values[0][31].strip()
    return icon_to_number(icon)

def get_snow(date):
    date_snow_df = weymouth_weather_df[weymouth_weather_df['datetime'] == date]
    #print(date_snow_df.dtypes)
    snowdepth = date_snow_df.values[0][15] 
    if snowdepth == None:
        return 0
    else:
        return int(snowdepth)

def mlpregressor(x_train, y_train, x_test, y_test):
    # mlp = MLPRegressor(hidden_layer_sizes=150, solver='lbfgs', max_iter=10000, activation='identity', random_state=0, learning_rate_init=0.001, verbose='True', momentum=0.9, tol=0.0001, early_stopping=False)
    mlp = MLPRegressor(hidden_layer_sizes=150, solver='adam', max_iter=10000, activation='relu', random_state=0, learning_rate_init=0.001, verbose='True', momentum=0.9, tol=0.0001, early_stopping=False)

    mlp.fit(x_train, y_train)

    y_guess = mlp.predict(x_test)

    print(sqrt(mean_squared_error(y_test, y_guess)), r2_score(y_test, y_guess))

    return mlp

def knn(x_train, y_train, x_test, y_test):
    
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

def rand_forest(x_train, y_train, x_test, y_test):
    regressor = RandomForestRegressor(n_estimators=50, max_features="auto", bootstrap=True, oob_score=False, random_state=0)
    regressor.fit(x_train, y_train)
    y_guess = regressor.predict(x_test)
    print(sqrt(mean_squared_error(y_test, y_guess)), r2_score(y_test, y_guess))
    
    return regressor

from sklearn import linear_model
def ridge(x_train, y_train, x_test, y_test):
    reg = linear_model.Ridge()
    reg.fit(x_train, y_train)
    y_guess = reg.predict(x_test)
    print(sqrt(mean_squared_error(y_test, y_guess)), r2_score(y_test, y_guess))
    return reg

def train_model():
    weather()
    off_peak_times()
    seasons()

    df['arrival_diff'] = df.apply(lambda row : (datetime.strptime((row['arr_at']).strip(), '%H:%M') - datetime.strptime((row['pta']).strip(), '%H:%M')).total_seconds()/60  if row['arr_at'] != None and row['pta'] != None else None, axis=1)
    print(df.info())

    filtered_df = df[df['arr_at'].notnull() & df['pta'].notnull()]

    print(filtered_df.iloc[:,27])

    filtered_df["precipitation"] = filtered_df["precipitation"].astype(object).astype(float)

    Y = filtered_df.iloc[:,27]

    X = filtered_df.iloc[:,[21,22,23,24,25,26]]

    print(filtered_df.info())
    
    print(X)
    scaler = StandardScaler()
    scaler.fit(X)

    Xtrain, Xtest, Ytrain, Ytest = train_test_split(X,Y, test_size=0.1, random_state=1)

    Xtrain = scaler.transform(Xtrain)
    Xtest = scaler.transform(Xtest)
    prediction_model = rand_forest(Xtrain, Ytrain, Xtest, Ytest)
    return prediction_model, scaler
    

def get_arrival_time(prediction_model, scaler, begin_station, destination_station, left_time_string, delay_amount):
    a = estimate_time_difference()
    arrival_time = calculate_arrival_time(begin_station, destination_station, left_time_string, delay_amount, a, prediction_model, scaler)
    return arrival_time

if __name__ == '__main__':
    #trained, scaler = train_model()
    #joblib.dump(trained, "./random_forest.joblib")
    #joblib.dump(scaler, "./scaler.joblib")
    
    #weather()
    #off_peak_times()
    #seasons()
    #x = df.loc[[4,42374,79414,186735,314590]]
    #107446, 117601, 120426, 150580
    #print(x)
    #print(x.iloc[:,[0,21]])
    #print(df.iloc[21,22,23,24])
    
    
    delay = timedelta(minutes=10)
    
    loaded_rf = joblib.load("./random_forest.joblib")
    scaler = joblib.load("./scaler.joblib")
    x = datetime(2000, 10,10,8,10)
    print(get_arrival_time(loaded_rf, scaler, 'DCH', 'WEY', x, delay))
    
    
    
    
    
    
