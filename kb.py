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


def set_response(message):
    global response
    response = message


class Booking(KnowledgeEngine):
    @DefFacts()
    def _initial_action(self):
        set_response('Can not comprehend')
        if 'reset' in self.dictionary:
            if self.dictionary.get('reset') == 'true':
                self.knowledge = {}
                self.dictionary['service'] = 'chat'

        # Get Service
        service = self.dictionary.get('service')
        if 'service' in self.knowledge:
            if service != 'chat':
                name = self.knowledge.get('name')
                self.knowledge = {}
                self.knowledge['name'] = name
                self.knowledge['service'] = service
        else:
            self.knowledge['service'] = service
        yield Fact(service=self.knowledge.get('service'))

        # Set knowledge
        if not 'question' in self.knowledge:
            self.knowledge['question'] = str()

        if 'name' in self.knowledge:
            yield Fact(name=self.knowledge.get('name'))
        if 'isReturn' in self.knowledge:
            yield Fact(isReturn=self.knowledge.get('isReturn'))
        if 'fromLocation' in self.knowledge:
            yield Fact(fromLocation=self.knowledge.get('fromLocation'))
        if 'toLocation' in self.knowledge:
            yield Fact(toLocation=self.knowledge.get('toLocation'))

        if 'departDate' in self.knowledge:
            yield Fact(departDate=self.knowledge.get('departDate'))
        if 'departTime' in self.knowledge:
            yield Fact(departTime=self.knowledge.get('departTime'))
        if 'returnDate' in self.knowledge:
            yield Fact(returnDate=self.knowledge.get('returnDate'))
        if 'returnTime' in self.knowledge:
            yield Fact(returnTime=self.knowledge.get('returnTime'))

        if 'givenTicket' in self.knowledge:
            yield Fact(givenTicket=self.knowledge.get('givenTicket'))
        if 'whatsNext' in self.knowledge:
            yield Fact(whatsNext=self.knowledge.get('whatsNext'))

        if 'predictFromLocation' in self.knowledge:
            yield Fact(predictFromLocation=self.knowledge.get('predictFromLocation'))
        if 'predictToLocation' in self.knowledge:
            yield Fact(predictToLocation=self.knowledge.get('predictToLocation'))
        if 'predictDepartTime' in self.knowledge:
            yield Fact(predictDepartTime=self.knowledge.get('predictDepartTime'))
        if 'predictReturnTime' in self.knowledge:
            yield Fact(predictReturnTime=self.knowledge.get('predictReturnTime'))
        if 'predictDelay' in self.knowledge:
            yield Fact(predictDelay=self.knowledge.get('predictDelay'))
        if 'informationGiven' in self.knowledge:
            yield Fact(informationGiven=self.knowledge.get('informationGiven'))

    @Rule(salience=1)
    def message_greeting(self):
        if 'greeting' in self.dictionary:
            set_response(nlp.greeting_output)

    '''
    @Rule(salience=2)
    def message_service_selected(self):
        if 'booking' in self.dictionary:
            set_response("You have selected booking")
        if 'ticket info' in self.dictionary:
            set_response("You have selected ticket information")
        if 'delays' in self.dictionary:
            set_response("You have selected delays service")
    '''


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
