import pandas as pd
from datetime import datetime
import requests
from io import StringIO
import argparse


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
    returned = requests.post(webhook_url ,json={'text':msg_string})    


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

    return(full_message)


def main():

    parser = argparse.ArgumentParser(description='Parses a Google Sheets file containing a meeting schedule')
    parser.add_argument('--webhook_url', type=str, help='Webhook URL from Slack')
    parser.add_argument('--drive_file_id',type=str, help='File ID on Google Drive')
    args = parser.parse_args()

    print("Webhook URL:" + args.webhook_url)
    print("Google Drive file ID:" + args.drive_file_id)

    schedule = pull_schedule(args.drive_file_id)
    next_session = parse_tsv(schedule)
    msg = create_message(next_session)
    send_message(msg, args.webhook_url)
    print(msg)


if __name__ == "__main__":
    main()


