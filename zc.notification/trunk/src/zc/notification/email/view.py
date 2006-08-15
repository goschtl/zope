from email.MIMENonMultipart import MIMENonMultipart
from email.MIMEMultipart import MIMEMultipart
from email import Charset
from email.Header import Header

from zope import i18n, component, interface
import zope.app.security.interfaces

import zc.notification.interfaces
import zc.notification.email.notifier

def translate(msgid, domain=None, mapping=None, context=None,
              target_language=None, default=None):
    if mapping is not None:
        msgid = zope.i18nmessageid.Message(msgid, mapping=mapping)
    return i18n.translate(
        msgid, domain, mapping, context, target_language, default)

UTF8 = Charset.Charset('utf-8')
UTF8.body_encoding = Charset.QP

class UTF8MIMEText(MIMENonMultipart):
    def __init__(self, _text, _subtype='plain'):
        MIMENonMultipart.__init__(self, 'text', _subtype, charset='utf-8')
        self.set_payload(_text, UTF8)

class EmailView(object):

    interface.implements(
        zc.notification.email.interfaces.IEmailView)

    component.adapts(
        zc.notification.interfaces.INotification,
        zope.app.security.interfaces.IPrincipal)

    renderHTML = None

    def __init__(self, context, principal):
        self.context = context
        self.principal = principal

    def render(self):
        self.mapping = self.context.mapping
        if self.mapping is not None:
            res = {}
            for k, v in self.mapping.items():
                if isinstance(v, basestring):
                    if isinstance(v, zope.i18nmessageid.Message):
                        v = i18n.translate(v, context=self.principal)
                    res[k] = v
            self.mapping = res
        msg = translate(
            self.context.message, mapping=self.mapping,
            context=self.principal)
        if self.context.summary is not None:
            summary = translate(
                self.context.summary, mapping=self.mapping,
                context=self.principal)
        else:
            parts = msg.split('\n', 1)
            if len(parts) == 1:
                summary = msg
                rest = ''
            else:
                summary, rest = parts
            if len(summary) > 53:
                summary = summary[:50] + "..."
            else:
                msg = rest.strip()

        body = UTF8MIMEText(msg.encode("utf8"))
        if self.renderHTML is None:
            body['Subject'] = Header(summary.encode("utf8"), 'utf-8')
            return body.as_string()
        else:
            self.message = msg
            self.summary = summary
            html = UTF8MIMEText(self.renderHTML(), 'html')
            multi = MIMEMultipart('alternative', None, (body, html))
            multi['Subject'] = Header(summary, UTF8)
            multi.epilogue = ''
            return multi.as_string()

