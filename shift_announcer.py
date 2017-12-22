#!/bin/python3

import argparse
from email.mime.text import MIMEText
import subprocess
from subprocess import Popen, PIPE
import csv
from collections import defaultdict
from enum import IntEnum


class LogLevel(IntEnum):
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERR = 4
log_level = None


def main():

    desc = 'Script to send out announcement emails for shift schedules.'
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--templateFile', type=str, default='template.txt',
                        help="Path to file containing template of email body.")
    parser.add_argument('--csvFile', type=str, default='test_file.csv',
                        help="CSV file containing DOC names and \
                        assigned dates.")
    parser.add_argument('--fromField', type=str,
                        default="cms-l1t-technical-coordination@cern.ch",
                        help="E-Mail address to be put into 'From:' field.")
    parser.add_argument('--logLevel', type=str, default='INFO',
                        help="Log level. \
                        (One of 'DEBUG', 'INFO', 'WARN', 'ERR'.)")
    parser.add_argument('--go_time', action='store_true')
    opts = parser.parse_args()

    global log_level
    log_level = LogLevel[opts.logLevel]

    doc_schedule = defaultdict(list)
    with open(opts.csvFile, newline='') as csvfile:
        r = csv.reader(csvfile, delimiter=",", quotechar="|")
        for row in r:
            name = row[0]
            date = row[1]
            if(len(date) > 0):
                doc_schedule[name].append(date)
            else:
                doc_schedule[name].extend([])
                debug("Date field is empty.")
            debug(doc_schedule)

    for name, dates in doc_schedule.items():
        email = get_email_address(name)
        if email is None:
            err("No e-mail address assigned to DOC. Skipping!")
            continue
        debug(name + " " + email + " " + str(dates))

        with open(opts.templateFile) as template_file:
            mail_body = template_file.read()
        mail_body = mail_body.replace("$$name$$", name)

        if(len(dates) > 0):
            dates_string = "You were assigned the following weeks:\n"
            dates_string += "\n".join(dates)
            dates_string += "\n\n"
            dates_string += "If this doesn't work for you feel free to send \
an e-mail to the L1 DOC list cms-trigger-field-managers@cern.ch to arrange \
a swap with one of the other DOCs."
        else:
            dates_string = "In this first period you were not assigned any \
shifts."
        mail_body = mail_body.replace("$$dates$$", dates_string)

        msg = MIMEText(mail_body, "plain", "utf-8")
        msg["From"] = opts.fromField
        msg["CC"] = opts.fromField
        msg["To"] = email
        msg["Subject"] = "L1 DOC assignment for 2018."

        debug(str(msg))

        if opts.go_time:
            info("Sending message.. ")
            p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
            p.communicate(msg.as_bytes())


def get_email_address(name):
    emails = subprocess.check_output(["/bin/phonebook", "--terse", "email",
                                      name],
                                     universal_newlines=True).splitlines()

    mail_index = 0
    info("Current DOC: " + name)
    debug(emails)
    debug(len(emails))
    if len(emails) == 0:
        print("No e-mail address found for " + name +
              ". Please indicate which to use. Press enter to skip.")
        manual_email = input("--> ")
        if len(manual_email.strip()) > 0:
            emails.append(manual_email)
    if len(emails) > 1:
        print("Multiple e-mail addresses found for " + name +
              ". Please indicate which to use. Enter -1 to skip.")
        for email in enumerate(emails):
            print(str(email[0]) + "\t" + email[1])

        mail_index = int(input("--> "))
    if mail_index == -1 or len(emails) == 0:
        return None
    selected_address = emails[mail_index].strip(";")
    info("Selected " + selected_address)
    return selected_address


def debug(msg):
    if log_level <= LogLevel.DEBUG:
        print("DEBUG: " + str(msg))


def info(msg):
    if log_level <= LogLevel.INFO:
        print("INFO: " + msg)


def warn(msg):
    if log_level <= LogLevel.WARN:
        print("WARNING: " + msg)


def err(msg):
    if log_level <= LogLevel.ERR:
        print("ERROR: " + msg)

if __name__ == '__main__':
    main()
