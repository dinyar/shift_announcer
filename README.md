# shift_announcer.py

## Introduction

This is a script that can be used to send shift scheduling emails to on-calls at CERN. It reads in a csv file that contains in each row the name of the future shifter as well as one date (corresponding to a week) during which the person is on call. Duplicate entries are forseen in case of multiple on-call weeks, e.g.:

```
Anton Bruckner, 31.10.2018
Igor Stravinsky, 04.02.2018
Pierre Boulez, 13.05.2018
Richard Wagner,
Igor Stravinsky, 23.03.2018
```

The script will collect all names and group them. It will then query the CERN phonebook (via the `phonebook` command installed on CERN computers) to determine a future on-call person's e-mail address. If it finds multiple matches it will query to user for the correct one, likewise in case of no results the script will query for the address to use.

A template file will be used to create the message body, where `$$name$$` will be replaced by the name in the csv file and ``$$date$$`` will be replaced by a string of the form:

> You were assigned the following weeks:  
> [date 1]  
> [date 2]  
> [...]  
>  
> If this doesn't work for you feel free to send an e-mail to the L1 DOC list cms-trigger-field-managers@cern.ch to arrange a swap with one of the other DOCs.

or

> In this first period you were not assigned any shifts.

in case there were no entries with dates associated found (as with Richard Wagner in the above example).

## Usage

Usage of the script is fairly straightforward:

```
% python3 shift_announcer.py -h 
usage: shift_announcer.py [-h] [--templateFile TEMPLATEFILE]
                          [--csvFile CSVFILE] [--fromField FROMFIELD]
                          [--logLevel LOGLEVEL] [--go_time]

Script to send out announcement emails for shift schedules.

optional arguments:
  -h, --help            show this help message and exit
  --templateFile TEMPLATEFILE
                        Path to file containing template of email body.
                        (default: template.txt)
  --csvFile CSVFILE     CSV file containing DOC names and assigned dates.
                        (default: test_file.csv)
  --fromField FROMFIELD
                        E-Mail address to be put into 'From:' field. (default:
                        cms-l1t-technical-coordination@cern.ch)
  --logLevel LOGLEVEL   Log level. (One of 'DEBUG', 'INFO', 'WARN', 'ERR'.)
                        (default: INFO)
  --go_time             Actually send out the emails. (default: False)
```

In particular the `--go_time` option needs to be passed in order to actually send out emails. If this isn't passed the script will only construct the messages (and in `DEBUG` mode also output the contents onto the command line).
