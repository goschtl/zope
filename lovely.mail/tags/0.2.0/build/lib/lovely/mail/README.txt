Lovely.Mail and Mail Testing
============================

This package mainly provides a simple way to test the mail delivery using the
current configuration. There is no need to change the mailing configuration
for the functional tests.

  >>> from lovely.mail import testing

Before we can set up the mail testing we need to register the mailer
utilities.

  >>> from zope import component
  >>> from zope.sendmail.mailer import SMTPMailer
  >>> component.provideUtility(SMTPMailer(),
  ...                          name='lovely-mailer')

  >>> from zope.sendmail.delivery import QueuedMailDelivery
  >>> component.provideUtility(QueuedMailDelivery('some_path'),
  ...                          name='lovely-mail-delivery')

Now we set up testing. This is the code which should go into you
setUp-function for your tests.

  >>> testing.setUpSMTPTesting('lovely-mailer', 'lovely-mail-delivery', unit_test=True)

Testing simply replaces the smtp mailer of the utility to a test smtp mailer.

  >>> from zope.sendmail.interfaces import IMailer, IMailDelivery
  >>> mailer = component.getUtility(IMailer, 'lovely-mailer')
  >>> mailer.smtp
  <class 'lovely.mail.testing.TestMailerConnection'>

And the mail delivery gets a temporary directory.

  >>> delivery = component.getUtility(IMailDelivery, 'lovely-mail-delivery')
  >>> delivery._queuePath != 'some_path'
  True

Testing provides a list with already sent mails.

  >>> testing.sentMails
  []

Now we send a mail.

  >>> messageId = delivery.send('README', ['MAILQUEUE',], 'I am a testing mail')
  >>> testing.sentMails
  []

The mail is not sent yet because we need to trigger mail delivery.

  >>> testing.triggerMail()
  >>> from pprint import pprint
  >>> pprint(testing.sentMails)
  [('README',
   ('MAILQUEUE',),
   'Message-Id: <...>\nI am a testing mail')]


We also provide a simple function to send mails.

  >>> from lovely.mail import sendmail
  >>> sendmail('subject', 'me@gmail.org', ['you@gmail.org'], 'my mail body')
  >>> testing.sentMails = []
  >>> testing.triggerMail()
  >>> pprint(testing.sentMails)
  [('me@gmail.org',
    ('you@gmail.org',),
    'Message-Id: ...\nFrom: me@gmail.org\nTo: you@gmail.org\n...\nmy mail body')]

If we provide tuples for the addresses we get this :

  >>> sendmail('subject', ('ich', 'me@gmail.org'), [('du','you@gmail.org',)], 'my mail body')
  >>> testing.sentMails = []
  >>> testing.triggerMail()
  >>> pprint(testing.sentMails)
  [('ich <me@gmail.org>',
    ('du <you@gmail.org>',),
    'Message-Id: ...\nFrom: ich <me@gmail.org>\nTo: du <you@gmail.org>\n...\nmy mail body')]



And clean up.

  >>> testing.tearDownSMTPTesting()
  >>> mailer.smtp
  <class smtplib.SMTP at ...>
  >>> delivery._queuePath == 'some_path'
  True
  >>> testing.sentMails
  []

