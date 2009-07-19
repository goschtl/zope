##########################################################################
# zopyx.smartprintng.server
# (C) 2008, 2009, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
import email.MIMEText
import email.Header
import email.MIMEBase
import email.MIMEMultipart
from email import Encoders
from ConfigParser import ConfigParser
from zope.sendmail.mailer import SMTPMailer


def makeMailer():

    mail_config = os.environ.get('EMAIL_CONFIG')
    if not mail_config:
        raise RuntimeError('No email configuration found')
    if not os.path.exists(mail_config):
        raise RuntimeError('Configured email configuration file not available')

    CP = ConfigParser()
    CP.read('email.ini')

    hostname = 'localhost'
    username = None
    password = None
    no_tls = False
    force_tls = False

    if CP.has_option('mail', 'hostname'): hostname = CP.get('mail', 'hostname')
    if CP.has_option('mail', 'username'): username = CP.get('mail', 'username')
    if CP.has_option('mail', 'password'): password = CP.get('mail', 'password')
    if CP.has_option('mail', 'no_tls'): no_tls = CP.getboolean('mail', 'no_tls')
    if CP.has_option('mail', 'force_tls'): force_tls = CP.getboolean('mail', 'force_tls')

    return SMTPMailer(hostname=hostname,
                      username=username,
                      password=password,
                      no_tls=no_tls,
                      force_tls=force_tls)


def send_email(sender, recipient, subject, body, attachments=[]):

    try:
        mailer = makeMailer()
    except Exception,e:
        raise RuntimeError('Email configuration error (%s)' % e)

    msg = email.MIMEMultipart.MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = email.Header.Header(subject, 'UTF-8')
    msg.attach(email.MIMEText.MIMEText(body.encode('UTF-8'), 'plain', 'UTF-8'))

    for att in attachments:
        part = email.MIMEBase.MIMEBase('application', "octet-stream")
        part.set_payload(file(att, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 
                        'attachment; filename="%s"' % os.path.basename(att))
        msg.attach(part)

    mailer.send(sender, [recipient], msg.as_string())


