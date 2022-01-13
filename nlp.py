import spacy
from spacy.matcher import Matcher

nlp = spacy.load('en_core_web_lg')

greeting_input = ("hey", "hi", "good morning", "good evening", "morning", "evening")
greeting_output = "Hello, please reply with the service you would like, reply: booking, ticket info or delays"

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
    # Reference from : https://stackoverflow.com/questions/67113389/spacy-matcher-date-pattern-will-match-hyphens-but-not-forward-slashes
    ticketDate = None

    for ent in user.ents:
        if ent.label_ == "DATE":
            ticketDate = ent.text
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

    return ticketDate


def getTime(user):
    tickettime = None
    for ent in user.ents:
        if ent.label_ == "TIME":
            tickettime = ent.text
        else:
            matcher = Matcher(nlp.vocab)
            time = [{'IS_DIGIT': True}, {'ORTH': ':'}, {'IS_DIGIT': True}]
            matcher.add('time', [time])
            matches = matcher(user)

            for match_id, start, end in matches:
                tickettime = user[start:end].text
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

def getSimilarity(rule, user):
    similarity = rule.similarity(user)
    return similarity

def get_entities(message):
    message = nlp(message)

    kbdictionary = {}
    kbdictionary['service'] = 'chat'
    if str(message) in greeting_input:
        kbdictionary['greeting'] = 'true'

    if str(message) in agree_input:
        kbdictionary['answer'] = 'true'

    if str(message) in disagree_input:
        kbdictionary['answer'] = 'false'

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
