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
            print(greeting_output)

def agree(doc):
    for token in doc:
        if token.text.lower() in agree_input:
            print(agree_output)

def disagree(doc):
    for token in doc:
        if token.text.lower() in disagree_input:
            print(disagree_output)

def lemmatizaion(doc):
    for token in doc:
        print(token, token.lemma_)

def pos(doc):
    for token in doc:
        print(token, token.pos_)

def getinfo():
    while(True):
        user = input()
        user = nlp(user)

        lemmatizaion(user)
        pos(user)

        # Not sure should the matcher be in the knowledge base or nlp
        # To find the match 'from city' and 'to city' to know the departure and arrival station
        matcher = Matcher(nlp.vocab)
        fromStation = [{'LOWER': 'from'}, {'ENT_TYPE': 'GPE'}]
        matcher.add('from', [fromStation])
        matches = matcher(user)

        for match_id, start, end in matches:
            station1 = user[start:end].text
            print(station1)

        matcher2 = Matcher(nlp.vocab)
        toStation = [{'LOWER': 'to'}, {'ENT_TYPE': 'GPE'}]
        matcher2.add('to', [toStation])
        matches2 = matcher2(user)

        for match_id, start, end in matches2:
            station2 = user[start:end].text
            print(station2)

        greeting(user)
        agree(user)
        disagree(user)

        if user.text.lower() == "bye" or user.text.lower() == "thank you":
            break;

        for ent in user.ents:
            if ent.label_ == "GPE":
                city = ent.text
                print("City: ", city)
            elif ent.label_ == "DATE":
                date = ent.text
                print("Date: ", date)
            elif ent.label_ == "TIME":
                time = ent.text
                print("Time: ", time)

if __name__ == '__main__':
    getinfo()