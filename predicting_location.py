from os import stat
from pandas import *
import difflib
import unittest
import psycopg2

#conn = psycopg2.connect(database = 'train', user = 'postgres', password='meow', host='127.0.0.1', port='5432')
conn = psycopg2.connect(database = 'AIdatabase', user = 'postgres', password='account7248',host='127.0.0.1', port='5432')

cursor = conn.cursor()

cursor.execute('SELECT * FROM trainstation')

trainabbdata = cursor.fetchall()

data = DataFrame(trainabbdata, columns=['Station', 'Name', 'CRS Code'])

#data = read_csv("stationabb.csv")

stations = data['Station'].tolist()
stationsAbb = data['CRS Code']


def predict_location(location):
    uppercase_location = location.upper()
    close_matches = difflib.get_close_matches(uppercase_location, stations, 1, 0.85)
    if uppercase_location in stations:
        i = data.loc[data['Station'] == uppercase_location].index[0]
        stationAbb = stationsAbb[i]
        guessed_station = False
        # probably do not need guessed_station
        return uppercase_location, stationAbb, guessed_station
    elif len(close_matches) > 0:
        guessed_station = True
        i = data.loc[data['Station'] == close_matches[0]].index[0]
        stationAbb = stationsAbb[i]
        # add user confirm if station is correct
        # probably do not need guessed_station
        return close_matches[0], stationAbb, guessed_station
    else:
        for station in stations:
            stationAbb = data[data['Station'] == station].values[0][2]
            if len(uppercase_location) > 0:
                if uppercase_location in station and uppercase_location[0] in stationAbb:
                    return station, stationAbb, True
        
        return None, None, False


if __name__ == '__main__':
    # unittest.main()
    print('input: norwch')
    print(predict_location('nrowich'))
    print('-----------------')
    print('input: southampton')
    print(predict_location('southampton'))
    print('-----------------')
    print('input: victoria')
    print(predict_location('victoria'))
    print('-----------------')
    print('input: weymouth')
    print(predict_location('weymouth'))
    print('-----------------')
    print('input: sdsdsd')
    print(predict_location('sdsdsd'))
    print('-----------------')
    print('input: liverpool street')
    print(predict_location('liverpool street'))
    print('-----------------')
    print('input: waterloo')
    print(predict_location('waterloo'))
    print('-----------------')
    print('input: swansea')
    print(predict_location('swansea'))
