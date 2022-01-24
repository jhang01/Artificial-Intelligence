import dateparser
import dateutil
from dateutil import parser
import spacy
from spacy.matcher import Matcher

import kb
import predicting_location
from datetime import datetime

nlp = spacy.load('en_core_web_lg')

greeting_input = ("hey", "hi", "good morning", "good evening", "morning", "evening", "hello")
greeting_output = "Please could you provide us with a username, if you do not have one please reply with a " \
                  "desired username. "
reset_input = ("reset", "start again", "restart", "clear")

agree_input = ("yes", "yea", "yeah", "yh", "y", "true")
agree_output = ("Okay, let me check it for you.")

disagree_input = ("no", "wrong", "n", "false")
disagree_output = ("Could you please try rewording your message for me again?")

thanks_input = ("thanks", "thank you", "ty", "bye")
thanks_output = ("Happy to help!")

services_input = ("booking", "ticket info", "delays")

booking_input = {'travel', 'travels', 'book', 'booking', 'bookings', 'book tickets', 'book a ticket', 'book ticket', 'want to book a train ticket', 'want to book train', 'want to book a train', 'booking train ticket'}
delay_input = {'predict', 'prediction', 'delay', 'delays', 'train delay info', 'train delay information', 'train delay', 'get train delay info', 'get delay info'}
ticketInfo_input = {"ticket information", "ticket info", "information", "info", 'get ticket info'}
present_time_input = {"now", "right now", "immediately", "straight away"}

def greeting(doc):
    doc = nlp(doc)
    for token in doc:
        if token.text.lower() in greeting_input:
            return (greeting_output)


def agree(doc):
    doc = nlp(doc)
    for token in doc:
        if token.text.lower() in agree_input:
            return (agree_output)


def disagree(doc):
    doc = nlp(doc)
    for token in doc:
        if token.text.lower() in disagree_input:
            return (disagree_output)


def thanks(doc):
    doc = nlp(doc)
    for token in doc:
        if token.text.lower() in thanks_input:
            return (thanks_output)


def lemmatizaion(doc):
    doc = nlp(doc)
    for token in doc:
        print(token, token.lemma_)


def pos(doc):
    doc = nlp(doc)
    for token in doc:
        print(token, token.pos_)


def getDate(user):
    # Reference from : https://stackoverflow.com/questions/67113389/spacy-matcher-date-pattern-will-match-hyphens-but-not-forward-slashes
    user = nlp(user)
    ticketDate = None

    for ent in user.ents:
        if ent.label_ == "DATE":
            ticketDate = dateparser.parse(ent.text, settings={'DATE_ORDER': 'DMY', 'PREFER_DATES_FROM': 'future'},
                                          languages=['en'])  # uk chatbot so use DMY
            # ticketDate = str(ticketDate.day).zfill(2) + str(ticketDate.month).zfill(2) + (str(ticketDate.year)[2:])
            return ticketDate

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
        lastTwoYearDigit = ticketDate[-2:]
        if "/" in ticketDate:
            ticketDate = ''.join(i.zfill(2) for i in ticketDate.split('/'))
            ticketDate = '/'.join([ticketDate[i:i + n] for i in range(0, len(ticketDate), n)])
        elif "-" in ticketDate:
            ticketDate = ''.join(i.zfill(2) for i in ticketDate.split('-'))
            ticketDate = '/'.join([ticketDate[i:i + n] for i in range(0, len(ticketDate), n)])
        elif "." in ticketDate:
            ticketDate = ''.join(i.zfill(2) for i in ticketDate.split('.'))
            ticketDate = '/'.join([ticketDate[i:i + n] for i in range(0, len(ticketDate), n)])
        ticketDate = ticketDate[0:6] + firstTwoYearDigit + lastTwoYearDigit
        try:
            ticketDate = datetime.strptime(ticketDate, "%d/%m/%Y")
        except:
            ticketDate = None

    return ticketDate


def getTime(user):
    user = nlp(user)
    ticket_time = None

    if str(user) in present_time_input:
        print("Yes")
        ticket_time = datetime.now()
        return ticket_time

    for ent in user.ents:
        if ent.label_ == "TIME":
            ticket_time = dateparser.parse(ent.text, settings={'PREFER_DATES_FROM': 'future'})
            return ticket_time

    matcher = Matcher(nlp.vocab)
    time = [{'IS_DIGIT': True}, {'ORTH': ':'}, {'IS_DIGIT': True}]
    time2 = [{'TEXT': {'REGEX': r'^\d{1,2}:\d{1,2}$'}}]
    matcher.add('time', [time])
    matcher.add('time2', [time2])
    matches = matcher(user)

    if matches:
        for match_id, start, end in matches:
            ticket_time = user[start:end].text
            n = 2
            if ':' in ticket_time:
                ticket_time = ''.join(i.zfill(2) for i in ticket_time.split(':'))
                ticket_time = ':'.join([ticket_time[i:i + n] for i in range(0, len(ticket_time), n)])

            date_plus_tme = "01/01/01 " + ticket_time
            try:
                ticket_time = datetime.strptime(date_plus_tme, "%d/%m/%y %H:%M")
            except:
                ticket_time = None

        return ticket_time




def getcity(user):
    departure = None
    arrival = None

    # matcher = Matcher(nlp.vocab)
    # fromStation = [{'LOWER': 'from'}, {'ENT_TYPE': 'GPE', 'OP': '*'}]
    # fromStation2 = [{'LOWER': 'from'}, {'POS': 'PROPN', 'OP': '*'}]
    # matcher.add('from', [fromStation])
    # matcher.add('from2', [fromStation2])
    # matches = matcher(user)
    #
    # for match_id, start, end in matches:
    #     departure = user[start:end].text

    if " from " in (" " + user + " ") and " to " in (" " + user + " "):
        dleft = 'from '
        dright = ' to '
        departure = (user[user.index(dleft) + len(dleft):user.index(dright)])

    # matcher2 = Matcher(nlp.vocab)
    # toStation = [{'LOWER': 'to'}, {'ENT_TYPE': 'GPE', 'OP': '*'}]
    # toStation2 = [{'LOWER': 'to'}, {'POS': 'PROPN', 'OP': '*'}]
    # matcher2.add('to', [toStation])
    # matcher2.add('to2', [toStation2])
    # matches2 = matcher2(user)
    #
    # for match_id, start, end in matches2:
    #     arrival = user[start:end].text

    if " to " in (" " + user + " "):
        arrival = user.partition(' to ')[2]

    return departure, arrival


def getSimilarity(rule, user):
    similarity = rule.similarity(user)
    return similarity


def get_entities(message):
    message = message.lower()
    message = message.strip()
    message = nlp(message)

    kbdictionary = {}
    kbdictionary['service'] = 'chat'

    if str(message) in greeting_input:
        kbdictionary['greeting'] = 'true'

    if str(message) in agree_input:
        kbdictionary['answer'] = 'true'

    if str(message) in disagree_input:
        kbdictionary['answer'] = 'false'

    if kb.hasUsername is False:
        if len(str(message).split()) == 1 and 'greeting' not in kbdictionary:
            kbdictionary['name'] = str(message)

    locations = []
    locations_abbreviation = []
    fromStation, toStation = getcity(str(message))

    if fromStation:
        fromStation = fromStation
        station_name, station_abbreviation, guessed = predicting_location.predict_location(fromStation)
        if station_name:
            locations.append(station_name)
            locations_abbreviation.append(station_abbreviation)
            if guessed:
                kbdictionary['guessedFrom'] = 'true'
            else:
                kbdictionary['guessedFrom'] = 'false'

    if toStation:
        toStation = toStation
        station_name, station_abbreviation, guessed = predicting_location.predict_location(toStation)
        if station_name:
            locations.append(station_name)
            locations_abbreviation.append(station_abbreviation)
            if guessed:
                kbdictionary['guessedTo'] = 'true'
            else:
                kbdictionary['guessedTo'] = 'false'

    if len(locations) > 1:
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



    if str(message) in delay_input:
        kbdictionary['service'] = 'predict'

    if str(message) in booking_input:
        kbdictionary['service'] = 'book'

    if str(message) in ticketInfo_input:
        kbdictionary['service'] = 'info'

    if str(message) in reset_input:
        kbdictionary['reset'] = 'true'

    print(kbdictionary)

    return kbdictionary


if __name__ == '__main__':
    while (True):
        user = input()
        #user = nlp(user)

        rule = nlp("buy train ticket")

        # similarity = getSimilarity(rule, user)
        # print(similarity)

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

        d = getDate(user)
        if (d != None):
            print("Date: ", d)
        t = getTime(user)
        if (t != None):
            print("Time: ", t)
