#!/usr/bin/python3
import requests, sys, json
import configparser
from pathlib import Path
from bs4 import BeautifulSoup

class Eir:
    
    network_name = 'eir'
    network_homepage = 'eir.ie'
    char_limit = 480

    def __init__(self):
        self.session = requests.Session()
        self.logged_in = False
        
        self.remaining_texts = ""

        self.overall_balance = 0
        self.overall_limit = 0
        
        self.international_balance = 0
        self.international_limit = 0
        
        self.national_balance = 0
        self.national_limit = 0
                

        self.mobile_num = ""   

    def login(self, username, password):

        response = self.session.post('https://my.eir.ie/rest/brand/3/portalUser/authenticate', 
        data = {"emailAddress": username,
                "password": password
                }
        )

        json_data = json.loads(response.text)
        if json_data['statusCode'] == 0:
            self.logged_in = True
            self.mobile_num = self.get_mobile_num()
            return 'login successful'
        
        else:
            return 'login status' + json_data['status']

        

    def get_mobile_num(self):
        response = self.session.get('https://my.eir.ie/rest/secure/brand/3/portalUser/lines')
        json_data = json.loads(response.text)
        number =  (json_data['data']['pairingsList'][0]['number'])
        return '+353' + number[1:]

    def send_webtext(self, message_text, recipient_number):

        response = self.session.post('https://my.eir.ie/mobile/webtext/mobileNumbers/' + self.mobile_num + '/messages',
                         json={"content": message_text,"recipients":[recipient_number]}
        )

        self.get_remaining_webtexts()
    
        return response.status_code
    
    def get_remaining_webtexts(self):
        response = self.session.get('https://my.eir.ie/mobile/webtext/mobileNumbers/' + self.mobile_num)
        json_data = json.loads(response.text)
        
        self.overall_balance = json_data['limits'][0]['balance']
        self.overall_limit = json_data['limits'][0]['limit']
        
        self.international_balance = json_data['limits'][1]['balance']
        self.international_limit = json_data['limits'][1]['limit']
        
        self.national_balance = json_data['limits'][2]['balance']
        self.national_limit = json_data['limits'][2]['limit']

        self.remaining_texts = ("National: " + str(self.national_balance) + "/" + str(self.national_limit) + "\n" +
                               "International: " + str(self.international_balance) + "/" + str(self.international_limit) + "\n" +
                               "Overall: " + str(self.overall_balance) + "/" + str(self.overall_limit) + "\n")
    


class Three:
    
    network_name = 'three'
    network_homepage = 'three.ie'
    char_limit = 765

    def __init__(self):
        self.session = requests.Session()
        self.logged_in = False
        self.remaining_texts = 0
    
    def login(self, username, password):

        response = self.session.post('https://login.three.ie/', 
        data = {'username': username,
            'password': password,
            'section':'section'
            }
        )
        
        soup = BeautifulSoup(response.text, 'html.parser')
        login_error =  soup.find('div', class_='loginError')
        
        if login_error is None:
            self.logged_in = True
            return 'login successful'
        else:
            return login_error.contents[0].text

    def send_webtext(self, message_text, recipient_number):

        response = self.session.post('https://messaging.three.ie/messages/send',
                         data={'APIID':'AUTH-WEBSSO',
                               'TargetApp':'o2om_smscenter_new.osp?MsgContentID=-1&SID=_',
                               '_token':'',
	                           'message':message_text,
                               'recipients_contacts[]':'tel:' +
                               recipient_number,
                               'scheduled_datetime':'',
                               'scheduled':''
                         },
        )

        self.remaining_texts = self.get_remaining_webtexts(response.text)
    
        return response.status_code
    
    @staticmethod  
    def get_remaining_webtexts(html_text_to_parse):
        soup = BeautifulSoup(html_text_to_parse, "html.parser")
        elements = soup.find_all('div', class_='user-crumb' )
    
        return elements[0].contents[0].text

def network_factory(network_name):
    
    if network_name == 'three':
        return Three()
    elif network_name == 'eir':
        return Eir()
