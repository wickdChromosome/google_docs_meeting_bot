# google_docs_meeting_bot

[![Build Status](https://travis-ci.com/wickdChromosome/google_docs_meeting_bot.svg?branch=master)](https://travis-ci.com/wickdChromosome/google_docs_meeting_bot)
[![GitHub Issues](https://img.shields.io/github/issues/wickdchromosome/loadmonitor.svg)](https://github.com/wickdchromosome/loadmonitor/issues)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)


## Description 

This is an example bot to show parsing a schedule (such as a schedule for group meetings), and using a webhook to send out a notification and a poll for the next meeting date in the schedule from today.

## Dependencies

You can install all dependencies by doing:

```
pip3 install -r requirements.txt
```

## Usage

This script uses a public google sheets schedule, where it is assumed that the first column in the document is the meeting date. First, you will need the ID of the google sheet you want to parse, and comment out
all unnecessary lines (that are not part of the schedule table) with a "#".

For an example input schedule, see an __Example schedule:__ https://docs.google.com/spreadsheets/d/1mmlQc6fOPfE044YtShJUIPTz6bODJwHo_rWXdBmqHLQ/edit#gid=0


Lets take something like this as an example:
```
python3 src/meeting_poll.py --webhook_url $WEBHOOK_URL --drive_file_id $FILE_ID --speaker_col 1 --presentation_col 2
```
- __webhook_url__ contains a webhook URL from Slack which you can get by creating a Slack app and adding a webhook for the channel you want to send the notifications to
- __drive_file_id__ is the ID of the file on google drive which you want to parse. As an example, in the url *https://docs.google.com/spreadsheets/d/1mmlQc6fOPfE044YtShJUIPTz6bODJwHo_rWXdBmqHLQ/edit#gid=0*, *1mmlQc6fOPfE044YtShJUIPTz6bODJwHo_rWXdBmqHLQ* is the file ID.
- __speaker_col__ is the index(zero based) of the column where the name of the speaker is for each date.
- __presentation_col__ is the index(zero based) of the column where a comma separated list of presentations can be found.

### Using cron jobs

If you wanted to send out a poll every week, you could copy the python script to __/usr/local/bin/__:
```
sudo cp src/meeting_poll.py /usr/local/bin/ && sudo chmod +x /usr/local/bin/meeting_poll.py
```

Then, you could add the following to your __etc/anacrontab__(assuming you are using anacron):
```
7       10      meeting_poll    meeting_poll.py --webhook_url $WEBHOOK_URL...
```

This will parse the meeting doc every week, and send out the polls/notifications to Slack.


