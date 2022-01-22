import random

from experta import *
from experta.watchers import RULES, AGENDA
import dateutil.parser
from datetime import datetime

import delay_prediction
import kb
from web_scrapper import Ticket
import nlp
from random import choice
import app
import predicting_location
from datetime import timedelta

global response
global username
global error_response
global user_message
global hasUsername

def set_hasUsername():
    global hasUsername
    hasUsername = False

def change_hasUsername():
    global hasUsername
    hasUsername = True

def set_username(user):
    global username
    username = user

def set_response(message):
    global response
    response = response + "@/" + message


def set_user_message(message):
    global user_message
    user_message = message


class Booking(KnowledgeEngine):
    @DefFacts()
    def _initial_action(self):
        global response
        response = ""
        # to do add reset to nlp
        if 'reset' in self.dictionary:  # if the dictionary contains reset
            if self.dictionary.get('reset') == 'true':
                print("Reseted chatbot")
                self.knowledge = {}
                self.dictionary['service'] = 'chat'

        # Get Service
        service = self.dictionary.get('service')  # get service stored
        name = self.knowledge.get('name')

        if 'service' in self.knowledge:  # check if an existing service is already active
            if service != 'chat':  # check if service is to chat
                self.knowledge = {}
                self.knowledge['service'] = service
                if name:
                    self.knowledge['name'] = name
                # create new knowledge with name and service
        else:
            self.knowledge['service'] = service  # if no service then set as service #default chat
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

        if 'fromLocationAbb' in self.knowledge:
            print(self.knowledge.get('fromLocationAbb'))
            yield Fact(fromLocationAbb=self.knowledge.get('fromLocationAbb'))
        if 'toLocationAbb' in self.knowledge:
            print(self.knowledge.get('toLocationAbb'))
            yield Fact(toLocationAbb=self.knowledge.get('toLocationAbb'))

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

        if 'leaveDate' in self.knowledge:
            print(self.knowledge.get('leaveDate'))
            yield Fact(leaveDate=self.knowledge.get('leaveDate'))

        if 'returnDateDT' in self.knowledge:
            print(self.knowledge.get('returnDateDT'))
            yield Fact(returnDateDT=self.knowledge.get('returnDateDT'))

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
        if 'predictFromLocationAbb' in self.knowledge:
            print(self.knowledge.get('predictFromLocationAbb'))
            yield Fact(predictFromLocationAbb=self.knowledge.get('predictFromLocationAbb'))
        if 'predictToLocationAbb' in self.knowledge:
            print(self.knowledge.get('predictToLocationAbb'))
            yield Fact(predictToLocationAbb=self.knowledge.get('predictToLocationAbb'))
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

    @Rule(NOT(Fact(service='chat')),
          salience=100)  # higher number priority
    def message_greeting(self):
        if 'greeting' in self.dictionary:
            set_response("Hi :)")

    ##remake name class
    # Ask Name
    @Rule(NOT(Fact(name=W())),
          salience=99)
    def ask_name(self):
        if 'name' in self.dictionary:
            name = self.dictionary.get('name')
            if (name in nlp.booking_input) or (name in nlp.delay_input):  # need to add duplicate for database
                set_response(
                    "The name you entered '" + name + "' cannot be assigned as an username. You're now assigned as a guest user.")
                name = "guest"
                set_username(name)
                change_hasUsername() # set to true
                self.declare(Fact(name=name))
                self.knowledge['name'] = name
            else:
                set_response("Hello " + name)
                set_username(name)
                change_hasUsername()
                self.declare(Fact(name=name))
                self.knowledge['name'] = name
        else:
            if self.knowledge['question'] == 'ask_name':
                set_response("Hello again :)")
                # setresponse for duplicate username
            else:
                self.knowledge['question'] = 'ask_name'
                set_response("Hi :)")
            set_response(nlp.greeting_output)
            self.declare(Fact(isQuestion=True))


    # Ask Service
    @Rule(Fact(service='chat'),
          Fact(name=MATCH.name),
          NOT(Fact(isQuestion=W())),
          salience=98)
    def ask_if_booking(self, name):
        if self.knowledge['question'] == 'ask_if_booking':
            set_response("Sorry, I did not understand what you meant by " + user_message)
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
            station_abbreviation = self.dictionary.get('station_abbreviation')
            self.declare(Fact(fromLocationAbb=station_abbreviation[0]))
            self.knowledge['fromLocationAbb'] = station_abbreviation[0]
            self.declare(Fact(toLocationAbb=station_abbreviation[1]))
            self.knowledge['toLocationAbb'] = station_abbreviation[1]
            self.declare(Fact(fromLocation=location[0]))
            self.knowledge['fromLocation'] = location[0]
            self.declare(Fact(toLocation=location[1]))
            self.knowledge['toLocation'] = location[1]
            del self.dictionary['location']
        else:
            if self.knowledge['question'] == 'ask_location':
                set_response("Please specify where you would like to travel from and to, for example 'from london "
                             "liverpool street to cambridge'")

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
            if departDate.date() < datetime.today().date():
                set_response("Sorry you have entered a date in the past")
                error = True
            else:
                self.declare(Fact(leaveDate=departDate))  # stores a datetime version of variable
                self.knowledge['leaveDate'] = departDate
                toDate = str(departDate.day).zfill(2) + str(departDate.month).zfill(2) + (str(departDate.year)[2:])
                self.declare(Fact(departDate=toDate))
                self.knowledge['departDate'] = toDate

        if self.knowledge['question'] == 'ask_depart_date' and departDate == 'false' and not error:
            set_response("Please provide a valid date")
        else:
            self.knowledge['question'] = 'ask_depart_date'

        if departDate == 'false' or error:
            set_response("Which date would you like to travel on")
            self.declare(Fact(isQuestion=True))

    # Ask Depart Time
    @Rule(Fact(service='book'),
          NOT(Fact(isQuestion=W())),
          NOT(Fact(departTime=W())),
          Fact(leaveDate=MATCH.leaveDate),
          salience=95)
    def ask_depart_time(self, leaveDate):
        error = False
        departTime = 'false'
        if 'times' in self.dictionary:
            departTime = self.dictionary.get('times')[0]

            if leaveDate.date() == datetime.now().date() and (departTime.hour < datetime.now().hour or (
                    departTime.hour == datetime.now().hour and departTime.minute < datetime.now().minute)):
                set_response("You have entered a time that has already past. Train depart time must be at the present or future time")
                error = True
            else:
                toTime = str(departTime.hour).zfill(2) + str(departTime.minute).zfill(2)
                self.declare(Fact(departTime=toTime))
                self.knowledge['departTime'] = toTime
                del self.dictionary['times']

        if self.knowledge['question'] == 'ask_depart_time' and departTime == 'false' and not error:
            set_response("Please provide a valid time")
        else:
            self.knowledge['question'] = 'ask_depart_time'

        if departTime == 'false' or error:
            set_response("What time would you like the train to leave?")
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
                set_response("Please let me know if you would like to book a return journey")
            else:
                self.knowledge['question'] = 'ask_is_return'
            set_response("Would you like to book a return journey?")
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
            if len(returnDate) > 1:
                returnDate = returnDate[1]
            else:
                returnDate = returnDate[0]
            if returnDate.date() < self.knowledge.get('leaveDate').date():
                set_response("The date you entered for your return journey is before you departure date. I am many "
                             "things but not a time machine. Please could you enter a date after your departure date")
                error = True
            else:
                self.declare(Fact(returnDateDT=returnDate))  # stores a datetime version of variable
                self.knowledge['returnDateDT'] = returnDate
                toDate = str(returnDate.day).zfill(2) + str(returnDate.month).zfill(2) + (str(returnDate.year)[2:])
                self.declare(Fact(returnDate=toDate))
                self.knowledge['returnDate'] = toDate

        if self.knowledge['question'] == 'ask_return_date' and returnDate == 'false' and not error:
            set_response("Please enter a valid date")
        else:
            self.knowledge['question'] = 'ask_return_date'

        if returnDate == 'false' or error:
            set_response("Which date would you like to return")
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
            if len(returnTime) > 1:
                returnTime = returnTime[1]
            else:
                returnTime = returnTime[0]
            toTime = str(returnTime.hour).zfill(2) + str(returnTime.minute).zfill(2)
            self.declare(Fact(returnTime=toTime))
            self.knowledge['returnTime'] = toTime
        else:
            if self.knowledge['question'] == 'ask_return_time':
                set_response("Please enter a valid time")
            else:
                self.knowledge['question'] = 'ask_return_time'
            set_response("What time would you like to return?")
            self.declare(Fact(isQuestion=True))

    # Show Single Ticket
    @Rule(Fact(service='book'),
          NOT(Fact(givenTicket=W())),
          Fact(isReturn='false'),
          Fact(fromLocation=MATCH.fromLocation),
          Fact(toLocation=MATCH.toLocation),
          Fact(departDate=MATCH.departDate),
          Fact(departTime=MATCH.departTime),
          Fact(leaveDate=MATCH.leaveDate),
          Fact(fromLocationAbb=MATCH.fromLocationAbb),
          Fact(toLocationAbb=MATCH.toLocationAbb),
          salience=91)
    def show_single_ticket(self, fromLocation, toLocation, departDate, departTime, leaveDate, fromLocationAbb, toLocationAbb):
        if 'givenTicket' not in self.knowledge:
            ticket = Ticket.get_ticket_single(fromLocationAbb, toLocationAbb, departDate, departTime)
            if not ticket:
                set_response(
                    "Sorry we failed to find an available ticket for you based on the information you have provided")
                self.declare(Fact(givenTicket=False))
                self.knowledge['givenTicket'] = False
            else:
                self.knowledge['url'] = ticket.get('url')
                set_response("The cheapest ticket we found is: " + "£{:,.2f}".format(ticket['ticketPrice']))
                set_response(" Train depart from: " + ticket['departureStationName'] +
                             " on: " + leaveDate.strftime('%b %d, %Y') +
                             " at " + ticket['departureTime'] +
                             " and arrive in " + ticket['arrivalStationName'] +
                             " at " + ticket['arrivalTime'] +
                             ". The total journey time is " + ticket['duration'] +
                             ". There will be " + ticket['changes'] + " number of changes.")
                set_response("Additional information: Tickets are for " + ticket['passenger'] +
                             ". This ticket is an " + ticket["ticketType"] + " ticket" +
                             ". Route information: " + ticket["description"] +
                             " Train service provided by " + ticket['fareProvider'] +
                             ". Ticket Restrictions: " + ticket['restrictions'])

                if ticket['warning'] != "None":
                    set_response("Warning: " + ticket['warning'])
                if ticket['status'] != "None":
                    set_response("Train status: " + ticket['status'])
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
          Fact(returnDateDT=MATCH.returnDateDT),
          Fact(leaveDate=MATCH.leaveDate),
          Fact(fromLocationAbb=MATCH.fromLocationAbb),
          Fact(toLocationAbb=MATCH.toLocationAbb),
          salience=90)
    def show_return_ticket(self, fromLocation, toLocation, departDate, departTime, returnDate, returnTime,
                           returnDateDT, leaveDate, fromLocationAbb, toLocationAbb):
        if 'givenTicket' not in self.knowledge:
            ticket = Ticket.get_ticket_return(fromLocationAbb, toLocationAbb, departDate, departTime, returnDate, returnTime)
            if not ticket:
                set_response("Sorry we failed to find a ticket based on the information you have provided")
                self.declare(Fact(givenTicket=False))
                self.knowledge['givenTicket'] = False
            else:
                self.knowledge['url'] = ticket.get('url')
                set_response("The cheapest ticket we found is: " + "£{:,.2f}".format(ticket['ticketPrice']))

                set_response("Departure ticket information: Train depart from " + ticket['departureStationName'] +
                             " on: " + leaveDate.strftime('%b %d, %Y') +
                             " at " + ticket['departureTime'] +
                             " and arrive in " + ticket['arrivalStationName'] +
                             " at " + ticket['arrivalTime'] +
                             ". The total journey time is " + ticket['duration'] +
                             ". There will be " + ticket['changes'] + " number of changes.")
                set_response("Additional information: Tickets are for " + ticket['passenger'] +
                             ". This ticket is an " + ticket["ticketType"] + " ticket" +
                             ". Route information: " + ticket["description"] +
                             " Train service provided by " + ticket['fareProvider'] +
                             ". Ticket Restrictions: " + ticket['restrictions'])

                if ticket['warning'] != "None":
                    set_response("Warning: " + ticket['warning'])
                if ticket['status'] != "None":
                    set_response("Train status: " + ticket['status'])

                set_response("Return ticket information: Train depart from: " + ticket['returnDepartureStationName'] +
                             " on: " + returnDateDT.strftime('%b %d, %Y') +
                             " at " + ticket['returnDepartureTime'] +
                             " and arrive in " + ticket['returnArrivalStationName'] +
                             " at " + ticket['returnArrivalTime'] +
                             ". The total journey time is " + ticket['returnDuration'] +
                             ". There will be " + ticket['returnChanges'] + " number of changes.")
                set_response("Additional information: Tickets are for " + ticket['returnPassenger'] +
                             ". This ticket is an " + ticket["returnTicketType"] + " ticket" +
                             ". Route information: " + ticket["returnDescription"] +
                             " Train service provided by " + ticket['returnFareProvider'] +
                             ". Ticket Restrictions: " + ticket['returnRestrictions'])

                if ticket['returnWarning'] != "None":
                    set_response("Warning: " + ticket['returnWarning'])
                if ticket['returnStatus'] != "None":
                    set_response("Train status: " + ticket['returnStatus'])

                self.declare(Fact(givenTicket=True))
                self.knowledge['givenTicket'] = True

    # Ask Confirm Booking
    @Rule(Fact(service='book'),
          Fact(givenTicket=True),
          salience=89)
    def confirm_booking(self):
        if 'answer' in self.dictionary:
            if self.dictionary.get('answer') == 'true':
                set_response("Please click on the following link to book your ticket")
                set_response("sendHyperLink:" + self.knowledge.get('url'))
            elif self.dictionary.get('answer') == 'false':
                set_response("To look for a new booking please type in 'book'.")
            self.knowledge['givenTicket'] = False
            self.declare(Fact(whatsNext=True))
            self.knowledge['whatsNext'] = True

            del self.dictionary['answer']
        else:
            if self.knowledge['question'] == 'confirm_booking':
                set_response("Please tell me if you want to book this ticket")
            else:
                self.knowledge['question'] = 'confirm_booking'
            set_response("Do you want to book this train ticket?")

    # Ask Predict Location
    @Rule(Fact(service='predict'),
          NOT(Fact(isQuestion=W())),
          NOT(Fact(predictFromLocation=W())),
          NOT(Fact(predictToLocation=W())),
          salience=88)
    def ask_predict_location(self):
        if 'location' in self.dictionary and len(self.dictionary.get('location')) > 1:
            location = self.dictionary.get('location')
            station_abbreviation = self.dictionary.get('station_abbreviation')
            self.declare(Fact(predictFromLocation=location[0]))
            self.knowledge['predictFromLocation'] = location[0]
            self.declare(Fact(predictToLocation=location[1]))
            self.knowledge['predictToLocation'] = location[1]
            self.declare(Fact(predictFromLocationAbb=station_abbreviation[0]))
            self.knowledge['preidctFromLocationAbb'] = station_abbreviation[0]
            self.declare(Fact(predictToLocationAbb=station_abbreviation[1]))
            self.knowledge['predictToLocationAbb'] = station_abbreviation[1]
            del self.dictionary['location']
        else:
            if self.knowledge['question'] == 'ask_predict_location':
                set_response("Please specify where you would like to travel from and to, for example 'from london liverpool street to cambridge'")
            else:
                self.knowledge['question'] = 'ask_predict_location'
            set_response("Where is the train going from and to.")
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
                set_response("ask predict time")
            else:
                self.knowledge['question'] = 'ask_predict_depart_time'
            set_response("Predict depart time")
            self.declare(Fact(isQuestion=True))

    # Ask Predict Return Time # if return
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
                set_response("ask predict return time")
            else:
                self.knowledge['question'] = 'ask_predict_return_time'
            set_response("Predict return time")
            self.declare(Fact(isQuestion=True))

    # Ask Delay
    @Rule(Fact(service='predict'),
          NOT(Fact(isQuestion=W())),
          NOT(Fact(predictDelay=W())),
          salience=85)
    def ask_predict_delay(self):
        if 'times' in self.dictionary:
            time = self.dictionary.get('times')[0]
            self.declare(Fact(predictDelay=time))
            self.knowledge['predictDelay'] = time
            self.declare(Fact(informationGiven=False))
            self.knowledge['informationGiven'] = False
            del self.dictionary['times']
        else:
            if self.knowledge['question'] == 'ask_predict_delay':
                set_response("Please provide a valid delay time")
            else:
                self.knowledge['question'] = 'ask_predict_delay'
            set_response("How long is your train delayed for?")
            self.declare(Fact(isQuestion=True))

    @Rule(Fact(service='predict'),
          Fact(informationGiven=False),
          Fact(depatureStationAbb=MATCH.depatureStationAbb),
          Fact(arrivalStationAbb=MATCH.arrivalStationAbb),
          salience=84)
    def predict_delay(self):
        #delay_prediction.get_arrival_time(trained, scale, "", "", "", "int")
        set_response("Response")
        self.knowledge['informationGiven'] = True
        self.declare(Fact(whatsNext=True))
        self.knowledge['whatsNext'] = True

    # Ask What's Next
    @Rule(Fact(whatsNext=True),
          salience=1)
    def whats_next(self):
        if 'answer' in self.dictionary:
            if self.dictionary.get('answer') == 'true':
                set_response("Which service would you like? For delay prediction type 'delay'. For ticket information "
                             "type 'info'. To make another booking "
                             "type 'book'.")
            elif self.dictionary.get('answer') == 'false':
                set_response("Goodbye.") # end convo here
                self.dictionary['reset'] = 'true'
            del self.dictionary['answer']
        else:
            if self.knowledge['question'] == 'whats_next':
                set_response("You can book another ticket, check delays or view ticket information. For delay prediction type 'delay'. For ticket information type 'info'. To make another booking type'book'.")
            else:
                self.knowledge['question'] = 'whats_next'
            set_response("Is there anything else I can help you with?")



# Initialize new booking
engine = Booking()
engine.knowledge = {}
set_hasUsername()
#trained, scale = delay_prediction.train_model()

# Set dictionary and run knowledge engine
def process_entities(entities):
    engine.dictionary = entities
    engine.reset()
    engine.run()


if __name__ == '__main__':
    # print(predicting_location.predict_location("Norwich"))
    print()
