import spacy
from spacy.matcher import Matcher
nlp = spacy.load('en_core_web_lg')

greeting_input = ("hey", "hi", "good morning", "good evening", "morning", "evening")
greeting_output = "Hello, how can I help you? :)"

agree_input = ("yes", "yea", "yeah", "yh", "y", "true")
agree_output = ("Okay, let me check it for you.")

disagree_input = ("no", "wrong", "n", "false")
disagree_output = ("Could you please try rewording your message for me again?")

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
    station1 = None
    station2 = None
    # Not sure should the matcher be in the knowledge base or nlp
    # To find the match 'from city' and 'to city' to know the departure and arrival station
    matcher = Matcher(nlp.vocab)
    fromStation = [{'LOWER': 'from'}, {'ENT_TYPE': 'GPE'}]
    matcher.add('from', [fromStation])
    matches = matcher(user)

    for match_id, start, end in matches:
        station1 = user[start:end].text

    matcher2 = Matcher(nlp.vocab)
    toStation = [{'LOWER': 'to'}, {'ENT_TYPE': 'GPE'}]
    matcher2.add('to', [toStation])
    matches2 = matcher2(user)

    for match_id, start, end in matches2:
        station2 = user[start:end].text

    if (station1 != None and station2 != None):
        return station1, station2
    elif(station1 == None):
        return None, station2
    elif(station2 == None):
        return station1, None
    else:
        return None, None

    return station1, station2

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

        station1, station2 = getcity(user)
        if (station1 != None):
            print(station1)
        if (station2 != None):
            print(station2)

        c = station(user)
        if (c != None):
            print(c)
        d = getDate(user)
        if (d != None):
            print("Date: ", d)
        t = getTime(user)
        if (t != None):
            print("Time: ", t)

        if user.text.lower() == "bye" or user.text.lower() == "thank you":
            break;