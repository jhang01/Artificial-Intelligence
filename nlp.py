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

text = ('Ticket from a city to another city')
doc = nlp(text)

while(True):
    user = input()
    user = nlp(user)

    matcher = Matcher(nlp.vocab)
    fromStation = [{'TEXT': 'from'}, {'ENT_TYPE': 'GPE'}]
    matcher.add('from', [fromStation])
    matches = matcher(user)

    print("matches found: ", len(matches))
    for match_id, start, end in matches:
        print("Match found:", user[start:end].text)

    greeting(user)
    agree(user)
    disagree(user)

    if user.text.lower() == "bye" or user.text.lower() == "thank you":
        break;

    city = []
    for ent in user.ents:
        #print(ent.text, ent.label_)
        if ent.label_ == "GPE":
            city.append(ent.text)
            print("City: ", city)
        elif ent.label_ == "DATE":
            date = ent.text
            print("Date: ", date)
        elif ent.label_ == "TIME":
            time = ent.text
            print("Time: ", time)