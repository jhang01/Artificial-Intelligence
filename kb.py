import random

from experta import *
from experta.watchers import RULES, AGENDA
import dateutil.parser
from datetime import datetime
from web_scrapper import Ticket
import nlp
from random import choice
import app
import predicting_location

global response
global user_message


def set_response(message):
    global response
    response = message


def set_user_message(message):
    global user_message
    user_message = message


class Booking(KnowledgeEngine):
    @DefFacts()
    def _initial_action(self):
        set_response('Can not comprehend')  # set initial response
        if 'reset' in self.dictionary:  # if the dictionary contains reset
            if self.dictionary.get('reset') == 'true':
                self.knowledge = {}
                self.dictionary['service'] = 'chat'

        # Get Service
        service = self.dictionary.get('service')  # get service stored
        if 'service' in self.knowledge:  # check if an existing service is already active
            if service != 'chat':  # check if service is to chat
                name = self.knowledge.get('name')  # keep the name of user
                self.knowledge = {'name': name, 'service': service}  # create new knowledge with name and service
        else:
            self.knowledge['service'] = service  # if no service then set as service
        print(self.knowledge.get('service'))
        yield Fact(service=self.knowledge.get('service'))

        # Set knowledge
        if 'question' not in self.knowledge:
            self.knowledge['question'] = str()
        else:
            print(self.knowledge.get('question'))
        if 'name' in self.knowledge:
            print(self.knowledge.get('name'))
            yield Fact(name=self.knowledge.get('name'))
        if 'isReturn' in self.knowledge:
            print(self.knowledge.get('isReturn'))
            yield Fact(isReturn=self.knowledge.get('isReturn'))
        if 'fromLocation' in self.knowledge:
            print(self.knowledge.get('fromLocation'))
            yield Fact(fromLocation=self.knowledge.get('fromLocation'))
        if 'toLocation' in self.knowledge:
            print(self.knowledge.get('toLocation'))
            yield Fact(toLocation=self.knowledge.get('toLocation'))

        if 'departDate' in self.knowledge:
            print(self.knowledge.get('departDate'))
            yield Fact(departDate=self.knowledge.get('departDate'))
        if 'departTime' in self.knowledge:
            print(self.knowledge.get('departTime'))
            yield Fact(departTime=self.knowledge.get('departTime'))
        if 'returnDate' in self.knowledge:
            print(self.knowledge.get('returnDate'))
            yield Fact(returnDate=self.knowledge.get('returnDate'))
        if 'returnTime' in self.knowledge:
            print(self.knowledge.get('returnTime'))
            yield Fact(returnTime=self.knowledge.get('returnTime'))

        if 'givenTicket' in self.knowledge:
            print(self.knowledge.get('givenTicket'))
            yield Fact(givenTicket=self.knowledge.get('givenTicket'))
        if 'whatsNext' in self.knowledge:
            print(self.knowledge.get('whatsNext'))
            yield Fact(whatsNext=self.knowledge.get('whatsNext'))

        if 'predictFromLocation' in self.knowledge:
            print(self.knowledge.get('predictFromLocation'))
            yield Fact(predictFromLocation=self.knowledge.get('predictFromLocation'))
        if 'predictToLocation' in self.knowledge:
            print(self.knowledge.get('predictToLocation'))
            yield Fact(predictToLocation=self.knowledge.get('predictToLocation'))
        if 'predictDepartTime' in self.knowledge:
            print(self.knowledge.get('predictDepartTime'))
            yield Fact(predictDepartTime=self.knowledge.get('predictDepartTime'))
        if 'predictReturnTime' in self.knowledge:
            print(self.knowledge.get('predictReturnTime'))
            yield Fact(predictReturnTime=self.knowledge.get('predictReturnTime'))
        if 'predictDelay' in self.knowledge:
            print(self.knowledge.get('predictDelay'))
            yield Fact(predictDelay=self.knowledge.get('predictDelay'))
        if 'informationGiven' in self.knowledge:
            print(self.knowledge.get('informationGiven'))
            yield Fact(informationGiven=self.knowledge.get('informationGiven'))

    @Rule(salience=100)  # higher number priority
    def message_greeting(self):
        if 'greeting' in self.dictionary:
            set_response(nlp.greeting_output)

    # Ask Name
    @Rule(Fact(service='chat'),
          NOT(Fact(name=W())),
          salience=99)
    def ask_name(self):
        if 'name' in self.dictionary:
            name = self.dictionary.get('name')
            self.declare(Fact(name=name))
            self.knowledge['name'] = name
        else:
            if self.knowledge['question'] == 'ask_name':
                set_response("We could not find user: " + user_message + "please provide us with your username")
            else:
                self.knowledge['question'] = 'ask_name'
                set_response(nlp.greeting_output)

    # Ask Service
    @Rule(Fact(service='chat'),
          Fact(name=MATCH.name),
          salience=98)
    def ask_if_booking(self, name):
        if self.knowledge['question'] == 'ask_if_booking':
            set_response("Sorry, I did not understand what you meant by " + user_message + ". Which service would you "
                                                                                           "like?")
        else:
            self.knowledge['question'] = 'ask_if_booking'
            set_response("Which service would you like? Available services: booking, ticket information, train delay "
                         "information")

    # Ask Location
    @Rule(Fact(service='book'),
          NOT(Fact(isQuestion=W())),
          NOT(Fact(fromLocation=W())),
          NOT(Fact(toLocation=W())),
          salience=97)
    def ask_location(self):
        error = False
        if 'location' in self.dictionary and len(self.dictionary.get('location')) > 1:
            location = self.dictionary.get('location')
            self.declare(Fact(fromLocation=location[0]))
            self.knowledge['fromLocation'] = location[0]
            self.declare(Fact(toLocation=location[1]))
            self.knowledge['toLocation'] = location[1]
        else:
            if self.knowledge['question'] == 'ask_location':
                set_response("Sorry I did not understand where " + user_message + " is. Please enter a valid station")
            else:
                self.knowledge['question'] = 'ask_location'
                set_response("Please specify where you would like to travel from and to")
            self.declare(Fact(isQuestion=True))

    # Ask Depart Date
    @Rule(Fact(service='book'),
          NOT(Fact(isQuestion=W())),
          NOT(Fact(departDate=W())),
          salience=96)
    def ask_depart_date(self):
        departDate = 'false'
        error = False
        if 'dates' in self.dictionary:
            departDate = self.dictionary.get('dates')[0]
            if dateutil.parser.parse(departDate) < datetime.now():
                set_response("Sorry you have entered a time in the past")
                error = True
            else:
                self.declare(Fact(departDate=departDate))
                self.knowledge['departDate'] = departDate

        if self.knowledge['question'] == 'ask_depart_date' and departDate == 'false' and not error:
            set_response("Response")
        else:
            self.knowledge['question'] = 'ask_depart_date'

        if departDate == 'false' or error:
            set_response("Which date would you like to travel on")
            self.declare(Fact(isQuestion=True))

    # Ask Depart Time
    @Rule(Fact(service='book'),
          NOT(Fact(isQuestion=W())),
          NOT(Fact(departTime=W())),
          salience=95)
    def ask_depart_time(self):
        if 'times' in self.dictionary:
            departTime = self.dictionary.get('times')
            self.declare(Fact(departTime=departTime[0]))
            self.knowledge['departTime'] = departTime[0]
            del self.dictionary['times']
        else:
            if self.knowledge['question'] == 'ask_depart_time':
                set_response("Response")
            else:
                self.knowledge['question'] = 'ask_depart_time'
                set_response("What time would you like to travel leave")
            self.declare(Fact(isQuestion=True))

    # Ask If Return
    @Rule(Fact(service='book'),
          NOT(Fact(isQuestion=W())),
          NOT(Fact(isReturn=W())),
          salience=94)
    def ask_is_return(self):
        if 'return' in self.dictionary:
            self.declare(Fact(isReturn='true'))
            self.knowledge['isReturn'] = 'true'
        elif 'answer' in self.dictionary:
            answer = self.dictionary.get('answer')
            self.declare(Fact(isReturn=answer))
            self.knowledge['isReturn'] = answer
            del self.dictionary['answer']
        else:
            if self.knowledge['question'] == 'ask_is_return':
                set_response("Response")
            else:
                self.knowledge['question'] = 'ask_is_return'
                set_response("Response")
            self.declare(Fact(isQuestion=True))

    # Ask Return Date
    @Rule(Fact(service='book'),
          NOT(Fact(isQuestion=W())),
          Fact(isReturn='true'),
          NOT(Fact(returnDate=W())),
          salience=93)
    def ask_return_date(self):
        returnDate = 'false'
        error = False
        if 'dates' in self.dictionary:
            returnDate = self.dictionary.get('dates')
            returnDate = returnDate[1] if len(returnDate) > 1 else returnDate[0]
            if dateutil.parser.parse(returnDate) < dateutil.parser.parse(self.knowledge.get('departDate')):
                set_response("Response")
                error = True
            else:
                self.declare(Fact(returnDate=returnDate))
                self.knowledge['returnDate'] = returnDate

        if self.knowledge['question'] == 'ask_return_date' and returnDate == 'false' and not error:
            set_response("Response")
        else:
            self.knowledge['question'] = 'ask_return_date'

        if returnDate == 'false' or error:
            set_response("Response")
            self.declare(Fact(isQuestion=True))

    # Ask Return Time
    @Rule(Fact(service='book'),
          NOT(Fact(isQuestion=W())),
          Fact(isReturn='true'),
          NOT(Fact(returnTime=W())),
          salience=92)
    def ask_return_time(self):
        if 'times' in self.dictionary:
            returnTime = self.dictionary.get('times')
            returnTime = returnTime[1] if len(returnTime) > 1 else returnTime[0]
            self.declare(Fact(returnTime=returnTime))
            self.knowledge['returnTime'] = returnTime
        else:
            if self.knowledge['question'] == 'ask_return_time':
                set_response("Response")
            else:
                self.knowledge['question'] = 'ask_return_time'
                set_response("Response")
            self.declare(Fact(isQuestion=True))

    # Show Single Ticket
    @Rule(Fact(service='book'),
          NOT(Fact(givenTicket=W())),
          Fact(isReturn='false'),
          Fact(fromLocation=MATCH.fromLocation),
          Fact(toLocation=MATCH.toLocation),
          Fact(departDate=MATCH.departDate),
          Fact(departTime=MATCH.departTime),
          salience=91)
    def show_single_ticket(self, fromLocation, toLocation, departDate, departTime):
        if not 'givenTicket' in self.knowledge:
            ticket = Ticket.get_ticket_single(fromLocation, toLocation, departDate, departTime)
            if not ticket:
                set_response("Response")
                self.declare(Fact(givenTicket=False))
                self.knowledge['givenTicket'] = False
            else:
                set_response("Response")
                self.knowledge['url'] = ticket.get('url')
                self.declare(Fact(givenTicket=True))
                self.knowledge['givenTicket'] = True

    # Show Return ticket
    @Rule(Fact(service='book'),
          NOT(Fact(givenTicket=W())),
          Fact(isReturn='true'),
          Fact(fromLocation=MATCH.fromLocation),
          Fact(toLocation=MATCH.toLocation),
          Fact(departDate=MATCH.departDate),
          Fact(departTime=MATCH.departTime),
          Fact(returnDate=MATCH.returnDate),
          Fact(returnTime=MATCH.returnTime),
          salience=90)
    def show_return_ticket(self, fromLocation, toLocation, departDate, departTime, returnDate, returnTime):
        if not 'givenTicket' in self.knowledge:
            ticket = Ticket.get_ticket_return(fromLocation, toLocation, departDate, departTime, returnDate, returnTime)
            if not ticket:
                set_response("Booking")
                self.declare(Fact(givenTicket=False))
                self.knowledge['givenTicket'] = False
            else:
                set_response("Booking")
                self.knowledge['url'] = ticket.get('url')
                self.declare(Fact(givenTicket=True))
                self.knowledge['givenTicket'] = True

    # Ask Confirm Booking
    @Rule(Fact(service='book'),
          Fact(givenTicket=True),
          salience=89)
    def confirm_booking(self):
        if 'answer' in self.dictionary:
            if self.dictionary.get('answer') == 'true':
                set_response("Booking")
            set_response("Response")
            self.knowledge['givenTicket'] = False
            self.declare(Fact(whatsNext=True))
            self.knowledge['whatsNext'] = True
            del self.dictionary['answer']
        else:
            if self.knowledge['question'] == 'confirm_booking':
                set_response("Booking")
            else:
                self.knowledge['question'] = 'confirm_booking'
            set_response("Booking")

    # Ask Predict Location
    @Rule(Fact(service='predict'),
          NOT(Fact(isQuestion=W())),
          NOT(Fact(predictFromLocation=W())),
          NOT(Fact(predictToLocation=W())),
          salience=88)
    def ask_predict_location(self):
        if 'location' in self.dictionary and len(self.dictionary.get('location')) > 1:
            location = self.dictionary.get('location')
            self.declare(Fact(predictFromLocation=location[0]))
            self.knowledge['predictFromLocation'] = location[0]
            self.declare(Fact(predictToLocation=location[1]))
            self.knowledge['predictToLocation'] = location[1]
            del self.dictionary['location']
        else:
            if self.knowledge['question'] == 'ask_predict_location':
                set_response("Response")
            else:
                self.knowledge['question'] = 'ask_predict_location'
                set_response("Response")
            self.declare(Fact(isQuestion=True))

    # Ask Predict Depart Time
    @Rule(Fact(service='predict'),
          NOT(Fact(isQuestion=W())),
          NOT(Fact(predictDepartTime=W())),
          salience=87)
    def ask_predict_depart_time(self):
        if 'times' in self.dictionary:
            predictDepartTime = self.dictionary.get('times')
            self.declare(Fact(predictDepartTime=predictDepartTime[0]))
            self.knowledge['predictDepartTime'] = predictDepartTime[0]
            del self.dictionary['times']
        else:
            if self.knowledge['question'] == 'ask_predict_depart_time':
                set_response("Response")
            else:
                self.knowledge['question'] = 'ask_predict_depart_time'
                set_response("Response")
            self.declare(Fact(isQuestion=True))

    # Ask Predict Return Time
    @Rule(Fact(service='predict'),
          NOT(Fact(isQuestion=W())),
          NOT(Fact(predictReturnTime=W())),
          salience=86)
    def ask_predict_return_time(self):
        if 'times' in self.dictionary:
            predictReturnTime = self.dictionary.get('times')
            predictReturnTime = predictReturnTime[1] if len(predictReturnTime) > 1 else predictReturnTime[0]
            self.declare(Fact(predictReturnTime=predictReturnTime))
            self.knowledge['predictReturnTime'] = predictReturnTime
            del self.dictionary['times']
        else:
            if self.knowledge['question'] == 'ask_predict_return_time':
                set_response("Response")
            else:
                self.knowledge['question'] = 'ask_predict_return_time'
                set_response("Response")
            self.declare(Fact(isQuestion=True))

    # Ask Delay
    @Rule(Fact(service='predict'),
          NOT(Fact(isQuestion=W())),
          NOT(Fact(predictDelay=W())),
          salience=85)
    def ask_predict_delay(self):
        if 'minutes' in self.dictionary:
            minutes = self.dictionary.get('minutes')[0]
            self.declare(Fact(predictDelay=minutes))
            self.knowledge['predictDelay'] = minutes
            self.declare(Fact(informationGiven=False))
            self.knowledge['informationGiven'] = False
            del self.dictionary['minutes']
        else:
            if self.knowledge['question'] == 'ask_predict_delay':
                set_response("Response")
            else:
                self.knowledge['question'] = 'ask_predict_delay'
                set_response("Response")
            self.declare(Fact(isQuestion=True))

    @Rule(Fact(service='predict'),
          Fact(informationGiven=False),
          salience=84)
    def predict_delay(self):
        # To Do: Add Train Delay Prediction Component
        set_response("Response")
        self.knowledge['informationGiven'] = True
        self.declare(Fact(whatsNext=True))
        self.knowledge['whatsNext'] = True

    # Ask What's Next
    @Rule(Fact(whatsNext=True),
          salience=83)
    def whats_next(self):
        if self.knowledge['question'] == 'whats_next':
            set_response("Response")
        else:
            self.knowledge['question'] = 'whats_next'
        set_response("Response")


# Initialize new booking
engine = Booking()
engine.knowledge = {}


# Set dictionary and run knowledge engine
def process_entities(entities):
    engine.dictionary = entities
    engine.reset()
    engine.run()


if __name__ == '__main__':
    # print(predicting_location.predict_location("Norwich"))
    print()
