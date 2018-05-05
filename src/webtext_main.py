#!/usr/bin/python3

import sys, configparser, readline
from pathlib import Path
import networks, pasteboard
from optparse import OptionParser

SMS = 0
MMS = 1

#returns username and password
def read_username_and_password():

    if(network.network_name not in config):
        #Must create .ini file (or add details to it)
        config_username = input( network.network_name + ' username: ')
        config_password = input( network.network_name + ' password: ')

        config[network.network_name] = { 'username' : config_username,
                            'password' : config_password }

        with open(path, 'w') as configfile:
            config.write(configfile)

    username = config[network.network_name]['username']
    password = config[network.network_name]['password']

    return [username, password]

#read_username_and_password

#returns the recipient's telephone number
def read_number():

    def listCompleter(text, state):
    
        line = readline.get_line_buffer()
        if not line: #no input yet - display all possibilities
            return [name + " " for c in names][state]

        else:
            return [name + " " for name in names if name.startswith(line)][state]
    #listCompleter(text, state)

    #create autocomplete options list from config file
    names = []
    for item in list(config.items('contacts')):
        names.append(item[0])

    #set up autocomplete
    readline.set_completer_delims('\t')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(listCompleter)

    if options.number == "":
    #prompt user for name or number
        recipient_number = input("Enter name or number:  ").strip()
    else:
        recipient_number = options.number

    #check if recipient starts with a digit
    if not recipient_number[0].isdigit():
    #look up name in contacts
        if not config.has_option('contacts', recipient_number):
            print("Cannot find contact: \"" + recipient_number +"\" in config file\nexiting")
            sys.exit()
        else:
            recipient_number = config['contacts'][recipient_number]

    return recipient_number

#read_number()

#returns text of message
def read_message(message_type):
    
    if message_type == SMS:
        if options.text == "":
            message_text = input("Enter message text: ")
        else:
            message_text = options.text

    elif message_type == MMS:
        if options.file == "":
            filename = input("Enter file name: ")
        else:
            filename = options.file

        #Do validation, assume file exists for now
        url = pasteboard.upload_image_file(filename)

        message_text = 'You have been sent an image, to view click this link: ' + url

    return message_text



#Command Line args
parser = OptionParser()

parser.add_option("-m", "--mms", action="store_true", dest="mms", help="used to send images", default=False)
parser.add_option("-s", "--sms", action="store_false", dest="mms", help="used to send text (default)", default=False)
parser.add_option("-n", "--number", "--name", dest="number", help="the recipient's telephone number, or their alias", default="")
parser.add_option("-t", "--text",  dest="text", help="the message text when using SMS", default="")
parser.add_option("-f", "--file",  dest="file", help="the file location when using MMS", default="")

(options, args) = parser.parse_args()

#create network object using factory
network = networks.network_factory('three')

#open ini file containing login details
path = str(Path.home()) + '/.webtext.ini'
config = configparser.ConfigParser()
config.read(path)

login_details = read_username_and_password()
username = login_details[0]
password = login_details[1]

recipient_number = read_number()

if(options.mms):
    message_text = read_message(MMS)
else:
    message_text = read_message(SMS)

#log in to network
print("logging in to "+ network.network_homepage + "...")
login_message = network.login(username, password)
print(login_message)
if not network.logged_in:
    sys.exit()

#send message(s)

if len(message_text) <= network.char_limit:
    print('sending webtext (1 of 1)...')
    network.send_webtext(message_text, recipient_number)
else:
    message_array = []
    
    while message_text:
        # allow 7 chars for (10/10) etc
        message_array.append(message_text[:network.char_limit - 7])
        message_text = message_text[network.char_limit - 7:]

    for message_num, message in enumerate(message_array, start=1):
        print('sending webtext (' + str(message_num) + ' of ' + str(len(message_array)) + ')...')
        message = '(' + str(message_num) + '/' + str(len(message_array)) + ')' + message
        network.send_webtext(message, recipient_number)

#print remaining webtexts
print ("webtext sent\nRemaining texts: " + network.remaining_texts)