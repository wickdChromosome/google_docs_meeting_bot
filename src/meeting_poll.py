#!/usr/bin/env python3

import pandas as pd
from datetime import datetime
import requests
from io import StringIO
import argparse

def pull_schedule(file_id):
    '''Downloads the group schedule from google drive'''

    returned = requests.get("https://docs.google.com/spreadsheets/export?id=" + file_id + "&exportFormat=tsv")
    
    return(returned.text)
 
def parse_tsv(pulled_schedule_str, speaker_col, topics_col):
    '''Parses the file downloaded from google drive'''

    pulled_schedule = StringIO(pulled_schedule_str)
    f = pd.read_csv(pulled_schedule ,sep='\t', comment='#')
    f.index = pd.DatetimeIndex(f[f.columns[0]])

    next_session = f[f.index > datetime.now()].head(1)

    speaker = next_session[next_session.columns[speaker_col]].tolist()[0]
    options = next_session[next_session.columns[topics_col]].tolist()[0].split(",")

    return([speaker, options])


def send_message(msg_string, webhook_url):
    '''Sends out the notification using a Slack webhook'''
    returned = requests.post(webhook_url ,json={'text':msg_string})    


def create_message(next_session):
    '''Creates the message to be sent to Slack'''
    emojis = [":grapes:",":melon:" ,":watermelon:" ,":tangerine:" ,":lemon:" ,":banana:" ,":pineapple:" ,":apple:" ,":green_apple:" ,":pear:" ,":peach:" ,":cherries:" ,":strawberry:" ,":kiwifruit:" ,":tomato:" ]

    [speaker, options] = next_session

    message1 = "`This week's speaker is: " + speaker + "!`\n"
    message = message1 + "*What should this week's journal club presentation be about? Available topics are:*\n\n"

    options_list = []

    num_options = len(options)
    #if there is only a single option, don't make a poll
    if num_options == 1:

        full_message = message + "Looks like there is only one offered talk this week: *" + options[0] + "*\n"
        return(full_message)

    #if there are no options, send a different message
    if num_options == 0:

        full_message = message + "Looks like there are no offered talks this week.\n"
        return(full_message)

    for i in range(len(options)):

        options_list.append(emojis[i] + " *-> " + options[i].strip(" ") + "*\n")

    options_list = "".join(options_list)

    full_message = message + options_list.replace(",","") 

    return(full_message)


def main():

    parser = argparse.ArgumentParser(description='Parses a Google Sheets file containing a meeting schedule')
    parser.add_argument('--webhook_url', required=True, type=str, help='Webhook URL from Slack')
    parser.add_argument('--drive_file_id', required=True, type=str, help='File ID on Google Drive')
    parser.add_argument('--speaker_col', required=True, type=str, help='Zero based index for the column containing the speaker names in the dataset')
    parser.add_argument('--presentation_col', required=True, type=str, help='Zero based index for the column containing the presentation options in the dataset')
    args = parser.parse_args()

    print("Webhook URL:" + args.webhook_url)
    print("Google Drive file ID:" + args.drive_file_id)

    schedule = pull_schedule(args.drive_file_id)
    next_session = parse_tsv(schedule, speaker_col=args.speaker_col, presentation_col=args.presentation_col)
    msg = create_message(next_session)
    send_message(msg, args.webhook_url)
    print(msg)


if __name__ == "__main__":
    main()


