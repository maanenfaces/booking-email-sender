#!/usr/bin/env python3

import argparse
import csv
import json
import logging
import os
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

# Logging level
LOG_LEVEL = int(os.getenv("LOG_LEVEL", logging.INFO))

# Gmail limits to 500 emails per day
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

logging.basicConfig(stream=sys.stdout, level=LOG_LEVEL)


def load_email_template_dir(dirname):
    data = {}
    with open(f"{dirname}/email.html", "r") as fd:
        data["html"] = str(fd.read())
    with open(f"{dirname}/email.txt", "r") as fd:
        data["text"] = str(fd.read())
    with open(f"{dirname}/metadata.json", "r") as fd:
        data["metadata"] = json.loads(fd.read())
    return data


def load_recipients_from_csv_file(filename):
    with open(filename, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        return [row for row in reader]


def send_email(email_tpl, recipients, opt_send=False):
    if opt_send:
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASSWORD)

    sender_email = email_tpl["metadata"]["sender_email"]
    sender_name = email_tpl["metadata"]["sender_name"]

    for recipient in recipients:
        message = MIMEMultipart()

        attrs = email_tpl["metadata"] | recipient
        contact_email = recipient["contact_email"]

        # Main mail content
        message['Subject'] = Header(
            email_tpl["metadata"]["email_title"].format(**attrs),
            'utf-8'
        )
        message['From'] = formataddr((
            str(Header(sender_name, 'utf-8')),
            sender_email
        ))
        message['To'] = contact_email

        # Reply To could be different
        message.add_header('reply-to', sender_email)

        # Attach mail content, first HTML et then txt version
        html = email_tpl["html"].format(**attrs)
        message.attach(MIMEText(html, 'html'))
        text = email_tpl["text"].format(**attrs)
        message.attach(MIMEText(text, 'plain'))

        logging.info(f"recipient_email = {contact_email}")
        logging.debug(message.as_string())

        if opt_send:
            server.sendmail(sender_email,[contact_email], message.as_string())

    if opt_send:
        server.quit()


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(
        description="Send formatted emails from selected template to all "
                    "recipients individually")
    parser.add_argument(
        "--csv",
        default=f"{script_dir}/recipients.csv",
        help="Path to CSV files containing the email addresses",
        type=str,
    )
    parser.add_argument(
        "--send",
        action="store_true",
        default=False,
        dest="send_flag",
        help="Send emails to recipients",
    )
    parser.add_argument(
        "--template",
        default="default",
        help="Name of the sub-directory under the \"templates\" directory",
        type=str,
    )
    args = parser.parse_args()

    logging.debug(f"LOG_LEVEL = {LOG_LEVEL}")
    logging.debug(f"SMTP_HOST = {SMTP_HOST}")
    logging.debug(f"SMTP_PORT = {SMTP_PORT}")
    logging.debug(f"SMTP_USER = {SMTP_USER}")

    if SMTP_PASSWORD:
        logging.debug(f"SMTP_PASSWORD = {SMTP_PASSWORD[0:4]}xxxx")
    else:
        logging.debug("SMTP_PASSWORD = None")

    logging.info(f"csv = {args.csv}")
    logging.info(f"send = {args.send_flag}")
    logging.info(f"template = {args.template}")

    template_dir = f"{script_dir}/templates/{args.template}"
    logging.info(f"template_dir = {template_dir}")

    if args.send_flag:
        print("\n!!!! IMPORTANT NOTICE !!!!\n"
              "SMTP is enabled. Emails will be sent to all recipients found "
              "in the CSV file.\nHit Ctrl-C keyboard keys within 5 seconds "
              "if you want to cancel.\n")
        for i in range(6):
            msg = f"{5 - i} second(s) remaining ." + "." * i
            print(msg, end="\r")
            time.sleep(1)

    logging.info("Processing...")
    send_email(
        load_email_template_dir(template_dir),
        load_recipients_from_csv_file(args.csv),
        args.send_flag
    )
