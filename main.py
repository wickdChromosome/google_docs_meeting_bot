import pandas as pd
from datetime import datetime
import requests
from io import StringIO

def pull_schedule(file_id):
    '''Downloads the group schedule from google drive and saves it as a file'''

    returned = requests.get("https://docs.google.com/spreadsheets/export?id=" + file_id + "&exportFormat=tsv")
    return(StringIO(returned.text))
 
def parse_tsv(pulled_schedule):
    '''Parses the file downloaded from google drive'''

    f = pd.read_csv(pulled_schedule ,sep='\t', comment='#')
    f.index = pd.DatetimeIndex(f["Date (red: not default)"])

    next_session = f[f.index > datetime.now()].head(1)

    return(next_session)

def send_message(msg_string, webhook_url):
    '''Sends out the notification using a Slack webhook'''
    returned = requests.post(webhook_url ,data={'text':msg_string})    


def create_message(next_session):
    '''Creates the message to be sent to Slack'''
    emojis = [":grapes:",":melon:" ,":watermelon:" ,":tangerine:" ,":lemon:" ,":banana:" ,":pineapple:" ,":apple:" ,":green_apple:" ,":pear:" ,":peach:" ,":cherries:" ,":strawberry:" ,":kiwifruit:" ,":tomato:" ]

    speaker = next_session['Speaker'].tolist()[0]
    message1 = "`This week's speaker is: " + speaker + "!`\n"
    message = message1 + "*What should this week's journal club presentation be about? Available topics are:*\n\n"

    options = next_session['Topic suggestions (poll on Monday)'].tolist()[0].split(",")
    options_list = []


    for i in range(len(options)):

        options_list.append(emojis[i] + " *-> " + options[i].strip(" ") + "*\n")

    options_list = "".join(options_list)

    full_message = message + options_list.replace(",","") 

    print(full_message)


schedule = pull_schedule("11iBubDlDrAGGvd3FkuSlBQxRvhoF4__BD32fS4AwsVE")
next_session = parse_tsv(schedule)
create_message(next_session)

