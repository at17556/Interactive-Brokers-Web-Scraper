import smtplib

from string import Template

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import os.path
import logging

LOGIN = 'hay.adrien@gmail.com'
FROM_ADDRESS = "HK IPO News <hay.adrien@gmail.com>"
PASSWORD = 'tppgmnkvleknacln'


def get_contacts(filename):
    """
    Return two lists names, emails containing names and email addresses
    read from a file specified by filename.
    """

    names = []
    emails = []
    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for a_contact in contacts_file:
            names.append(a_contact.split(",")[0])
            emails.append(a_contact.split(",")[1])
    return names, emails


def read_template(filename):
    """
    Returns a Template object comprising the contents of the 
    file specified by filename.
    """

    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)


def send(template, number_ipo, working_dir, attachment_dir):
    names, emails = get_contacts("{}/contacts.txt".format(working_dir))  # read contacts

    # file_location = attachment_dir + "/SupplementaryListingDocuments.png"
    file_location = attachment_dir + "/screenshot-hkexnews.png"

    if template == "no-ipo":
        message_template = read_template("{}/message_no-ipo.txt".format(working_dir))

    if template == "one-ipo":
        message_template = read_template("{}/message.txt".format(working_dir))

    if template == "multiple-ipo":
        message_template = read_template("{}/message.txt".format(working_dir))

    #if template == "error":
    #    message_template = read_template("{}/error.txt".format(working_dir))
    #    file_location = "/Users/athorn/Desktop/IB/IPO-Daily-Check_20190730/mylogs.log"

    if template == "error":
        message_template = read_template("{}/message_error.txt".format(working_dir))
        file_location = working_dir + "/ipo.log"



    # set up the SMTP server
    try:
        s = smtplib.SMTP(host='smtp.gmail.com', port=587)
        s.ehlo()
        s.starttls()
        s.login(LOGIN, PASSWORD)
    except:
        logging.error("Unable to Connect to SMTP Server")
        print("[ERROR] Unable to Connect to SMTP Server")
        exit()

    logging.info("Connection to SMTP server successful...")
    print("[INFO] Connection to SMTP server successful...")

    # For each contact, send the email:
    for name, email in zip(names, emails):
        msg = MIMEMultipart()  # create a message

        # add in the actual person name to the message template
        message = message_template.substitute(PERSON_NAME=name.title())

        # Prints out the message body for our sake
        #print("Email body: " + message)

        # setup the parameters of the message
        msg['From'] = FROM_ADDRESS
        msg['To'] = email
        msg['Subject'] = str(number_ipo) + " New IPO Document(s) Today"

        # add in the message body
        msg.attach(MIMEText(message, 'plain'))

        if os.path.isfile(file_location):
            filename = os.path.basename(file_location)
            attachment = open(file_location, "rb")
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

            msg.attach(part)
        else:
            logging.warning("Attachment File Not Found: " + file_location)
            print("[WARNING] Attachment File Not Found: " + file_location)



        # send the message via the server set up earlier.
        s.send_message(msg)
        del msg

        logging.info("Email has been sent to: " + email)
        print("[INFO] Email has been sent to: " + email)

    # Terminate the SMTP session and close the connection
    s.quit()


if __name__ == '__main__':
    send()