from pandas import *
import difflib

guessed_station = False

data = read_csv("stations.csv")

cities = data['name'].tolist()

def predict_location(location):
    close_matches = difflib.get_close_matches(location, cities, 1)
    if location in cities:
        return location
    elif len(close_matches) > 0:
        guessed_station = True
        return close_matches[0]
    else:
        return None
        

if __name__ == '__main__':
    print(predict_location("liverpool street".upper()))