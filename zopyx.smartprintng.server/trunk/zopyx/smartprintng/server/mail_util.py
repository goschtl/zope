##########################################################################
# zopyx.smartprintng.server
# (C) 2008, 2009, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import email.MIMEText
import email.Header
from ConfigParser import ConfigParser
from zope.sendmail.mailer import SMTPMailer

CP = ConfigParser(dict(hostname='localhost',
                       username=None,
                       password=None,
                       no_tls=False,
                       force_tls=False,
                       ))

CP.read('email.ini')

Mailer = SMTPMailer(hostname=CP.get('mail', 'hostname'),
                    username=CP.get('mail', 'username'),
                    password=CP.get('mail', 'password'),
                    no_tls=CP.getboolean('mail', 'no_tls'),
                    force_tls=CP.getboolean('mail', 'force_tls'))

def send_email(sender, recipient, subject, body):
    msg = email.MIMEText.MIMEText(body.encode('UTF-8'), 'plain', 'UTF-8')
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = email.Header.Header(subject, 'UTF-8')
    Mailer.send(sender, [recipient], msg.as_string())


