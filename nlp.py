import dateparser
import dateutil
from dateutil import parser
import spacy
from spacy.matcher import Matcher
import predicting_location
from datetime import datetime


nlp = spacy.load('en_core_web_lg')

greeting_input = ("hey", "hi", "good morning", "good evening", "morning", "evening", "hello")
greeting_output = "Please could you provide us with a username, if you do not have one please reply with a " \
                  "desired username. "

agree_input = ("yes", "yea", "yeah", "yh", "y", "true")
agree_output = ("Okay, let me check it for you.")

disagree_input = ("no", "wrong", "n", "false")
disagree_output = ("Could you please try rewording your message for me again?")

thanks_input = ("thanks", "thank you", "ty", "bye")
thanks_output = ("Happy to help!")

services_input = ("booking", "ticket info", "delays")


def greeting(doc):
    for token in doc:
        if token.text.lower() in greeting_input:
            return (greeting_output)


def agree(doc):
    for token in doc:
        if token.text.lower() in agree_input:
            return (agree_output)


def disagree(doc):
    for token in doc:
        if token.text.lower() in disagree_input:
            return (disagree_output)


def thanks(doc):
    for token in doc:
        if token.text.lower() in thanks_input:
            return (thanks_output)


def lemmatizaion(doc):
    for token in doc:
        print(token, token.lemma_)


def pos(doc):
    for token in doc:
        print(token, token.pos_)


def station(user):
    station = []
    for ent in user.ents:
        if ent.label_ == 'GPE':
            station.append(ent.text)
    return station


def getDate(user):
    # Reference from : https://stackoverflow.com/questions/67113389/spacy-matcher-date-pattern-will-match-hyphens-but-not-forward-slashes
    ticketDate = None

    for ent in user.ents:
        if ent.label_ == "DATE":
            ticketDate = dateparser.parse(ent.text,  settings={'DATE_ORDER': 'DMY'}, languages=['en']) # uk chatbot so use DMY
            #ticketDate = str(ticketDate.day).zfill(2) + str(ticketDate.month).zfill(2) + (str(ticketDate.year)[2:])
        else:
            matcher = Matcher(nlp.vocab)
            date1 = [{'TEXT': {'REGEX': r'^\d{1,2}/\d{1,2}/\d{2}(?:\d{2})?$'}}]
            date2 = [{'IS_DIGIT': True}, {'ORTH': '-'}, {'IS_DIGIT': True}, {'ORTH': '-'}, {'IS_DIGIT': True}]
            date3 = [{'TEXT': {'REGEX': r'^\d{1,2}.\d{1,2}.\d{2}(?:\d{2})?$'}}]

            matcher.add('date1', [date1])
            matcher.add('date2', [date2])
            matcher.add('date3', [date3])
            matches = matcher(user)

            for match_id, start, end in matches:
                ticketDate = user[start:end].text
                n = 2
                firstTwoYearDigit = str(datetime.today().year)
                firstTwoYearDigit = firstTwoYearDigit[0:2]
                if "/" in ticketDate:
                    ticketDate = ''.join(i.zfill(2) for i in ticketDate.split('/'))
                    ticketDate = '/'.join([ticketDate[i:i + n] for i in range(0, len(ticketDate), n)])
                elif "-" in ticketDate:
                    ticketDate = ''.join(i.zfill(2) for i in ticketDate.split('-'))
                    ticketDate = '-'.join([ticketDate[i:i + n] for i in range(0, len(ticketDate), n)])
                elif "." in ticketDate:
                    ticketDate = ''.join(i.zfill(2) for i in ticketDate.split('.'))
                    ticketDate = '.'.join([ticketDate[i:i + n] for i in range(0, len(ticketDate), n)])
                ticketDate = ticketDate[:-2] + firstTwoYearDigit + ticketDate[-2] + ticketDate[-1]
                ticketDate = datetime.strptime(ticketDate, "%d/%m/%Y")

    return ticketDate


def getTime(user):
    ticket_time = None
    for ent in user.ents:
        if ent.label_ == "TIME":
            ticket_time = dateparser.parse(ent.text, settings={'PREFER_DATES_FROM': 'future'})
        else:
            matcher = Matcher(nlp.vocab)
            time = [{'IS_DIGIT': True}, {'ORTH': ':'}, {'IS_DIGIT': True}]
            matcher.add('time', [time])
            matches = matcher(user)

            for match_id, start, end in matches:
                ticket_time = user[start:end].text
                ticket_time = datetime.combine(datetime.today(), ticket_time)

    return ticket_time

def getcity(user):
    departure = None
    arrival = None
    # Not sure should the matcher be in the knowledge base or nlp
    # To find the match 'from city' and 'to city' to know the departure and arrival station
    matcher = Matcher(nlp.vocab)
    fromStation = [{'LOWER': 'from'}, {'ENT_TYPE': 'GPE'}]
    matcher.add('from', [fromStation])
    matches = matcher(user)

    for match_id, start, end in matches:
        departure = user[start:end].text

    matcher2 = Matcher(nlp.vocab)
    toStation = [{'LOWER': 'to'}, {'ENT_TYPE': 'GPE'}]
    matcher2.add('to', [toStation])
    matches2 = matcher2(user)

    for match_id, start, end in matches2:
        arrival = user[start:end].text

    return departure, arrival


def getSimilarity(rule, user):
    similarity = rule.similarity(user)
    return similarity



def get_entities(message):
    message = message.lower()
    message = nlp(message)

    kbdictionary = {}
    kbdictionary['service'] = 'chat'

    if str(message) in greeting_input:
        kbdictionary['greeting'] = 'true'

    if str(message) in agree_input:
        kbdictionary['answer'] = 'true'

    if str(message) in disagree_input:
        kbdictionary['answer'] = 'false'

    hasName = False
    for entity in message.ents:
        if entity.label_ == 'PERSON':
            kbdictionary['name'] = entity.text
            hasName = True
    if not hasName and len(str(message).split()) == 1 and not ('greeting' in kbdictionary):
        kbdictionary['name'] = str(message)


    locations = []
    locations_abbreviation = []
    fromStation, toStation = getcity(message)

    if fromStation:
        fromStation = fromStation[5:]
        station_name, station_abbreviation, guessed = predicting_location.predict_location(str(fromStation))
        locations.append(station_name)
        locations_abbreviation.append(station_abbreviation)
        if guessed:
            kbdictionary['guessedFrom'] = 'true'
        else:
            kbdictionary['guessedFrom'] = 'false'

    if toStation:
        toStation = toStation[3:]
        station_name, station_abbreviation, guessed = predicting_location.predict_location(str(toStation))
        locations.append(station_name)
        locations_abbreviation.append(station_abbreviation)
        if guessed:
            kbdictionary['guessedTo'] = 'true'
        else:
            kbdictionary['guessedTo'] = 'false'

    if len(locations) > 0:
        kbdictionary['location'] = locations
        kbdictionary['station_abbreviation'] = locations_abbreviation

    dates = []
    times = []

    if getDate(message) is not None:
        dates.append(getDate(message))
    if getTime(message) is not None:
        times.append(getTime(message))

    if len(dates) > 0:
        kbdictionary['dates'] = dates
    if len(times) > 0:
        kbdictionary['times'] = times

    # Service/Is Return
    for token in message:
        token = str(token).lower()

        if token in {'predict', 'prediction', 'delay', 'delays'}:
            kbdictionary['service'] = 'predict'

        if token in {'travel', 'travels', 'book', 'booking', 'bookings'}:
            kbdictionary['service'] = 'book'

        if token in {'return', 'returns'}:
            kbdictionary['return'] = 'true'

    print(kbdictionary)

    return kbdictionary


if __name__ == '__main__':
    while (True):
        user = input()
        user = nlp(user)

        rule = nlp("buy train ticket")

        similarity = getSimilarity(rule, user)
        print(similarity)

        lemmatizaion(user)
        pos(user)

        greet = greeting(user)
        if (greet != None):
            print(greet)
        a = agree(user)
        if (a != None):
            print(a)
        dis = disagree(user)
        if (dis != None):
            print(dis)
        t = thanks(user)
        if (t != None):
            print(t)
            break

        departure, arrival = getcity(user)
        if (departure != None):
            print(departure)
        if (arrival != None):
            print(arrival)

        c = station(user)
        if (c != None):
            print(c)
        d = getDate(user)
        if (d != None):
            print("Date: ", d)
        t = getTime(user)
        if (t != None):
            print("Time: ", t)
