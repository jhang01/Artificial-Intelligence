from pandas import *
import difflib
import unittest

guessed_station = False

data = read_csv("stations.csv")

cities = data['name'].tolist()

def predict_location(location):
    uppercase_location = location.upper()
    close_matches = difflib.get_close_matches(uppercase_location, cities, 1, 0.7)
    if uppercase_location in cities:
        return uppercase_location
    elif len(close_matches) > 0:
        guessed_station = True
        return close_matches[0]
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