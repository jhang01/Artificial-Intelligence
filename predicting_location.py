from os import stat
from pandas import *
import difflib
import unittest

data = read_csv("stationabb.csv")

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


"""
data = read_csv("stations.csv")

citiesAbb = data['tiploc']

cities = data['name'].tolist()

def predict_location(location):
    uppercase_location = location.upper()
    close_matches = difflib.get_close_matches(uppercase_location, cities, 1, 0.85)
    if uppercase_location in cities:
        i = data.loc[data['name'] == uppercase_location].index[0]
        cityAbb = citiesAbb[i]
        guessed_station = False
        #probably do not need guessed_station
        return uppercase_location, cityAbb, guessed_station
    elif len(close_matches) > 0:
        guessed_station = True
        i = data.loc[data['name'] == close_matches[0]].index[0]
        cityAbb = citiesAbb[i]
        # add user confirm if station is correct
        # probably do not need guessed_station
        return close_matches[0], cityAbb, guessed_station
    else:
        length = len(uppercase_location)
        for station in cities:
            print(station[:length])
            if uppercase_location in station[:length]:
                cityAbb = data[data['name'] == station].values[0][3]
                return station, cityAbb, True
        return None, None, False

"""


class PredictLocationTest(unittest.TestCase):

    def test_same_name(self):
        self.assertEqual(predict_location('norwich')[1], 'NRW')

    def test_similar_name(self):
        self.assertEqual(predict_location('marke')[1], 'MSK')

    def test_similar_name(self):
        self.assertEqual(predict_location('southampton')[1], 'SOA')

    def test_not_found(self):
        self.assertEqual(predict_location('blaaa')[1], None)


if __name__ == '__main__':
    # unittest.main()
    print('input: norwch')
    print(predict_location('norwch'))
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
