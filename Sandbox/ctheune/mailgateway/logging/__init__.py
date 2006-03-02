import logging

logger = logging.getLogger('Mail')

def mail_log(event):
    event.received_by.append("log")
    message = "Received: to=\"%s\", from=\"%s\", msgid=\"%s\"" % \
            (event.mail['To'],
             event.mail['From'],
             event.mail['Message-Id'])
    logger.log(logging.INFO, message)
