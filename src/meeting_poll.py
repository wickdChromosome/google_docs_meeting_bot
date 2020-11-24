#!/usr/bin/env python3

import pandas as pd
from datetime import datetime
import requests
from io import StringIO
import argparse
import numpy as np
from collections import Counter
import sys
import random


def pull_schedule(file_id):
    '''Downloads the group schedule from google drive'''

    returned = requests.get("https://docs.google.com/spreadsheets/export?id=" + file_id + "&exportFormat=tsv")
    
    return(returned.text)
 
def parse_tsv(pulled_schedule_str, speaker_col, journal_col):
    '''Parses the file downloaded from google drive'''

    pulled_schedule = StringIO(pulled_schedule_str)
    f = pd.read_csv(pulled_schedule ,sep='\t', comment='#')
    f.index = pd.DatetimeIndex(f[f.columns[0]])

    next_session = f[f.index > datetime.now()].head(1)

    speaker = next_session[next_session.columns[speaker_col]].tolist()[0]

    #check if there is actually a list of items in that cell, instead of just nan
    optionsitem = next_session[next_session.columns[journal_col]].tolist()[0] 
    if type(optionsitem) != float:
        options = optionsitem.split(",")
    else:
        options = []

    return([speaker, options])


def send_message(msg_string, webhook_url):
    '''Sends out the notification using a Slack webhook'''
    returned = requests.post(webhook_url ,json={'text':msg_string})    


def create_message(next_session, group_map):
    '''Creates the message to be sent to Slack'''

    [speaker, journalspeaker] = next_session
    if speaker == '-':
        speaker = "No one"

    message = "*This week's speaker is: `" + speaker + "`*\n"

    #this still gets passed as a list bc of legacy stuff
    jspeaker = journalspeaker[0]
    if jspeaker == '-':
        jspeaker = "No one"

    message = message + "*This week's journal club will be held by:`" + jspeaker + '`*\n\n\n'


    ###THIS RANDOMIZATION STEP IS JUST LEFT IN TEMPORARILY AS IT PROVIDES UNFAIR BIAS
    #now make a randomized pair programming agenda for this week
    #create full list of languages, with counts

 #   pairprog_pairs = {}
    all_plangs = []
    #collect all occurrences of each programming language
    for plang_list in group_map.values():
        
        for plang in plang_list:

            all_plangs.append(plang)

    #now count the occurrences
    langscore_map = dict(Counter(all_plangs))

    ind_plang_scores = {}
    for ind in group_map.keys():
   
        #this maps the prog lang to a popularity score and sums it for the individual
        ind_plang_scores[ind] = np.sum([langscore_map[lang] for lang in group_map[ind]])


    #sort based on this score, so that people with the least popular
    #languages get assigned first
    sorted_people_dict = {k: v for k, v in sorted(ind_plang_scores.items(), key=lambda item: item[1])}

    #iterate over this list, randomly assigning another person that has at least one language in common
    #with this one

    ##ADDED RANDOMIZATION STEP TO SEE IF THIS MAKES THINGS MORE FAIR
    unpicked_people_list = list(sorted_people_dict.keys())
    random.shuffle(unpicked_people_list)
    

    message += "*The pair programming groups for this week are:*\n"

    for thisperson in unpicked_people_list:

        #exclude Pej
        if thisperson == 'Pejman':
            continue

        #get viable candidates
        known_languages = group_map[thisperson]
        viable_candidates = []

        for target_person in unpicked_people_list:

            #make sure its not the same ind
            if target_person == thisperson:
                continue

            #if there is at least one language in common, this is a viable candidate
            target_known_languages = group_map[target_person]
            if len(set(known_languages) & set(target_known_languages)) != 0:
                viable_candidates.append(target_person)


        #check to make sure that there is at least one viable candidate for this person
        if len(viable_candidates) == 0:
            sys.exit("No viable candidates available for " + thisperson)
               
        #now randomly pick a person from the viable options
        picked_person = random.choice(viable_candidates)

        #keep trying until a good choice is found
        tryc = 0
        while picked_person not in unpicked_people_list:

            picked_person = random.choice(viable_candidates)
            tryc += 1
            if tryc > 100:
                sys.exit("Unable to find pair for " + thisperson)


#        pairprog_pairs[thisperson] = picked_person
        #remove this person from the the list
        unpicked_people_list.remove(picked_person)
        unpicked_people_list.remove(thisperson)

        print("Removed " + thisperson)
        print("Removed " + picked_person)
        print(unpicked_people_list)

        message += "`" + thisperson + "` will show their code to `" + picked_person + '`\n'


    #now the last remaining pair
    if 'Pejman' in unpicked_people_list:
        unpicked_people_list.remove("Pejman")
        message += "`" + unpicked_people_list[0] + "` will show their code to `Pejman`\n"

    else:
        message += "`" + unpicked_people_list[0] + "` will show their code to `" + unpicked_people_list[1] + '`\n'


    message += '\n\n*The default time for code review sessions is Wednesday 2-3PM.*'

    return(message)


def main():

    parser = argparse.ArgumentParser(description='Parses a Google Sheets file containing a meeting schedule')
    parser.add_argument('--webhook_url', required=True, type=str, help='Webhook URL from Slack')
    parser.add_argument('--drive_file_id', required=True, type=str, help='File ID on Google Drive')
    parser.add_argument('--speaker_col', required=True, type=int, help='Zero based index for the column containing the speaker names in the dataset')
    parser.add_argument('--journalclub_col', required=True, type=int, help='Zero based index for the column containing the presentation holders name in the dataset')
    args = parser.parse_args()

    print("Webhook URL:" + args.webhook_url)
    print("Google Drive file ID:" + args.drive_file_id)

    schedule = pull_schedule(args.drive_file_id)
    next_session = parse_tsv(schedule, speaker_col=args.speaker_col, journal_col=args.journalclub_col)
    msg = create_message(next_session, group_map={'Bence' : ['Python','R']
                                                , 'Dan' : ['Python','R']
                                                , 'Pejman' : ['Python','R']
                                                , 'Marcela' : ['Python', 'R']
                                                , 'Nava' : ['Python', 'R']
                                                , 'Adam' : ['Python']
                                                , 'Eric' : ['Python', 'R']
                                                , 'Yuren' : ['Python']
                                                })
    send_message(msg, args.webhook_url)
    print(msg)


if __name__ == "__main__":
    main()


