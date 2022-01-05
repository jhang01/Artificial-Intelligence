import re

import spacy
from spacy.matcher import Matcher

nlp = spacy.load('en_core_web_lg')

greeting_input = ("hey", "hi", "good morning", "good evening", "morning", "evening")
greeting_output = "Hello, how can I help you? :)"

agree_input = ("yes", "yea", "yeah", "yh", "y", "true")
agree_output = ("Okay, let me check it for you.")

disagree_input = ("no", "wrong", "n", "false")
disagree_output = ("Could you please try rewording your message for me again?")

thanks_input = ("thanks", "thank you", "ty", "bye")
thanks_output = ("Happy to help!")

def greeting(doc):
    for token in doc:
        if token.text.lower() in greeting_input:
            return(greeting_output)

def agree(doc):
    for token in doc:
        if token.text.lower() in agree_input:
            return(agree_output)

def disagree(doc):
    for token in doc:
        if token.text.lower() in disagree_input:
            return(disagree_output)

def thanks(doc):
    for token in doc:
        if token.text.lower() in thanks_input:
            return(thanks_output)

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
    ticketDate = ""
    for ent in user.ents:
        if ent.label_ == "DATE":
            ticketDate = ent.text
    return ticketDate

def getTime(user):
    tickettime = ""
    for ent in user.ents:
        if ent.label_ == "TIME":
            tickettime = ent.text
    return tickettime


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

if __name__ == '__main__':
    while (True):
        user = input()
        user = nlp(user)

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
