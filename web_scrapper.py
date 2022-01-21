import requests, json
from bs4 import BeautifulSoup
from urllib import request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

import re


## requires chromedriver in same folder as chrome
# If you are using Chrome version 98, please download ChromeDriver 98.0.4758.48
# If you are using Chrome version 97, please download ChromeDriver 97.0.4692.71
# If you are using Chrome version 96, please download ChromeDriver 96.0.4664.45
class Ticket(object):
    url = str()

    @staticmethod
    def get_ticket_single(fromStation, toStation, departDate, departTime):
        parsed_html = Ticket.request_page_single(fromStation, toStation, departDate, departTime)
        return Ticket.get_cheapest_ticket(parsed_html, False, departDate, None)

    @staticmethod
    def get_ticket_return(fromStation, toStation, departDate, departTime, returnDate, returnTime):
        print(fromStation, toStation, departDate, departTime, returnDate, returnTime)
        parsed_html = Ticket.request_page_return(fromStation, toStation, departDate, departTime, returnDate, returnTime)
        return Ticket.get_cheapest_ticket(parsed_html, True, departDate, returnDate)

    @staticmethod
    def request_page_single(fromStation, toStation, departDate, departTime):
        fromStation = fromStation.replace(" ", "")
        toStation = toStation.replace(" ", "")
        url = ('http://ojp.nationalrail.co.uk/service/timesandfares/' + fromStation + '/' + toStation
               + '/' + departDate + '/' + departTime + '/dep')
        return Ticket.get_page_contents(url)

    @staticmethod
    def request_page_return(fromStation, toStation, departDate, departTime, returnDate, returnTime):
        fromStation = fromStation.replace(" ", "")
        toStation = toStation.replace(" ", "")
        url = ('http://ojp.nationalrail.co.uk/service/timesandfares/' + fromStation + '/' + toStation
               + '/' + departDate + '/' + departTime + '/dep/' + returnDate + '/' + returnTime + '/dep')
        return Ticket.get_page_contents(url)

    @staticmethod
    def get_page_contents(url):
        browser = webdriver.ChromeOptions()
        browser.headless = True
        ser = Service("C:/Program Files/Google/Chrome/Application/chromedriver.exe")
        driver = webdriver.Chrome(options=browser, service=ser)  # google chrome driver path
        driver.get(url)
        r = driver.page_source
        Ticket.url = url
        print(url)
        # r = requests.get(url)
        return BeautifulSoup(r, 'html.parser')

    @staticmethod
    def get_cheapest_ticket(page_contents, isReturn, departDate, returnDate):
        try:
            cheapest_ticket = page_contents.find('td', class_='fare has-cheapest')
            info = json.loads(cheapest_ticket.find('script', {'type': 'application/json'}).text)

            ticket = {}
            ticket['url'] = Ticket.url

            ticket['isReturn'] = isReturn
            ticket['departDate'] = departDate  #
            ticket['departureStationName'] = str(info['jsonJourneyBreakdown']['departureStationName'])  #
            ticket['arrivalStationName'] = str(info['jsonJourneyBreakdown']['arrivalStationName'])  #
            ticket['departureTime'] = str(info['jsonJourneyBreakdown']['departureTime'])  #
            ticket['arrivalTime'] = str(info['jsonJourneyBreakdown']['arrivalTime'])  #
            durationHours = str(info['jsonJourneyBreakdown']['durationHours'])  #
            durationMinutes = str(info['jsonJourneyBreakdown']['durationMinutes'])  #
            ticket['duration'] = (durationHours + 'h ' + durationMinutes + 'm')  #
            ticket['changes'] = str(info['jsonJourneyBreakdown']['changes'])  #

            ticket['warning'] = str(info['jsonJourneyBreakdown']['hoverInformation'])  #

            ticket['status'] = str(info['jsonJourneyBreakdown']['statusMessage'])  #

            ticket['ticketType'] = str(info['singleJsonFareBreakdowns'][0]['fareTicketType'])  #
            ticket['description'] = str(info['singleJsonFareBreakdowns'][0]['fareRouteDescription'])  #
            ticket['passenger'] = str(info['singleJsonFareBreakdowns'][0]['passengerType'])  #
            ticket['ticketPrice'] = info['singleJsonFareBreakdowns'][0]['ticketPrice']  #
            ticket['fareProvider'] = str(info['singleJsonFareBreakdowns'][0]['tocName'])  #
            ticket['restrictions'] = str(info['singleJsonFareBreakdowns'][0]['nreFareCategory'])  #

            if isReturn:
                return_content = page_contents.find('table', id='ift')
                if return_content.find('td', class_='fare has-cheapest'): #if has cheapest
                    return_cheapest_ticket = return_content.find('td', class_='fare has-cheapest')
                    return_info = json.loads(return_cheapest_ticket.find('script', {'type': 'application/json'}).text)
                else:
                    return_ticket_regex = re.compile('.*return-only default-select.*')  # gets selected default
                    return_cheapest_ticket = page_contents.find('div', {"class": return_ticket_regex})
                    return_info = json.loads(return_cheapest_ticket.find('script', {'type': 'text/javascript'}).text)

                ticket['returnDepartureStationName'] = str(return_info['jsonJourneyBreakdown']['departureStationName'])
                ticket['returnArrivalStationName'] = str(return_info['jsonJourneyBreakdown']['arrivalStationName'])
                ticket['returnDepartureTime'] = str(return_info['jsonJourneyBreakdown']['departureTime'])
                ticket['returnArrivalTime'] = str(return_info['jsonJourneyBreakdown']['arrivalTime'])
                ticket['returnDate'] = returnDate
                durationHours = str(return_info['jsonJourneyBreakdown']['durationHours'])
                durationMinutes = str(return_info['jsonJourneyBreakdown']['durationMinutes'])
                ticket['returnDuration'] = (durationHours + 'h ' + durationMinutes + 'm')
                ticket['returnChanges'] = str(return_info['jsonJourneyBreakdown']['changes'])
                ticket['returnWarning'] = str(return_info['jsonJourneyBreakdown']['hoverInformation'])
                ticket['returnStatus'] = str(return_info['jsonJourneyBreakdown']['statusMessage'])
                ticket['returnFareProvider'] = str(return_info['returnJsonFareBreakdowns'][0]['tocName'])
                ticket['returnTicketType'] = str(return_info['returnJsonFareBreakdowns'][0]['fareTicketType'])
                ticket['returnDescription'] = str(return_info['returnJsonFareBreakdowns'][0]['fareRouteDescription'])
                ticket['returnPassenger'] = str(return_info['returnJsonFareBreakdowns'][0]['passengerType'])
                ticket['returnRestrictions'] = str(return_info['returnJsonFareBreakdowns'][0]['nreFareCategory'])
                # ticket['ticketPrice'] = str(info['returnJsonFareBreakdowns'][1]['ticketPrice'])

            return ticket
        except:

            return False


if __name__ == '__main__':
    ticket = Ticket()
    # print(ticket.get_ticket_single("NRW", "CHM", "tomorrow", "0800"))
    # ticket.get_ticket_return("NRW", "CHM", "today", "1545", "tommorow", "1545")
    print(ticket.get_ticket_return("NRW", "CHM", "today", "1545", "tomorrow", "1545"))
