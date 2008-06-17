import email.Charset #See Phillip's book, p318 2nd Ed
email.Charset.add_charset('utf-8', email.Charset.SHORTEST, None, None)
from datetime import datetime
from email.MIMEText import MIMEText

from zope.component import getUtility, adapter
from zope.sendmail.interfaces import IMailDelivery

from zope.app.container.interfaces import IObjectAddedEvent

from grok.interfaces import IApplication

from grokstar.interfaces import IComment


@adapter(IComment, IObjectAddedEvent)
def notifyCommentAdded(comment, event):
        return commentAdded(comment)

def commentAdded(comment):
    message = MIMEText(comment.comment.encode('utf-8'), 'plain', 'utf-8')
    message['Subject'] = "Comment from " + comment.author
    recipient = getUtility(IApplication).email
    message['From'] = recipient
    message['To'] = recipient
    message['Date'] = datetime.now().strftime('%a, %e %b %Y %H:%M:%S %z')
    
    mailer = getUtility(IMailDelivery, 'grokstar')
    mailer.send(recipient, [recipient], message.as_string())
