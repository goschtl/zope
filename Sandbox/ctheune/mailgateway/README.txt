This is an experimental SMTP server for Zope using the twisted SMTP server.

When a mail comes in, an IMailReceivedEvent will be issued and you can read
the mail attribute which is a parsed RFC8288 message.

Original author: Christian Theune <ct@gocept.com>

Questions and comments are welcome.
