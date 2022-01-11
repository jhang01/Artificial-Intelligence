from pandas import *
import difflib
import unittest



data = read_csv("stations.csv")

citiesAbb = data['tiploc']

cities = data['name'].tolist()

def predict_location(location):
    uppercase_location = location.upper()
    close_matches = difflib.get_close_matches(uppercase_location, cities, 1, 0.7)
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
        return None





class PredictLocationTest(unittest.TestCase):

    def test_same_name(self):
        self.assertEqual(predict_location('norwich'), 'NORWICH')

    def test_similar_name(self):
        self.assertEqual(predict_location('marke'), 'MARSKE')
        
    def test_not_found(self):
        self.assertEqual(predict_location('blaaa'), None)
       

if __name__ == '__main__':
    # unittest.main()
    print('Input value: liverpool street')
    print('Output value: ' + predict_location("liverpool street") + '\n')
    print('Input value: norwich')
    print('Output value: ' + predict_location('norwich') + '\n')
    print('Input value: marke')
    print('Output value: ' + predict_location('marke') + '\n')
    print('Input value: blaaa')
    print('Output value: ' + str(predict_location('blaaa')))