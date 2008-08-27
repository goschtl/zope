##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Browser code for JS button demo.

$Id: layer.py 75942 2007-05-24 14:53:46Z srichter $
"""
__docformat__="restructuredtext"
import os.path
import zope.interface
from zope.viewlet.viewlet import CSSViewlet, JavaScriptViewlet
from zope.app.container.interfaces import INameChooser
from zope.traversing.browser import absoluteURL
from zope.security.proxy import removeSecurityProxy
from zope.session.interfaces import ISession
from z3c.form import form, button, field
from z3c.form.interfaces import IWidgets
from z3c.formui import layout
from z3c.formjs import jsaction, jsevent, ajax

from z3c.formjsdemo.chat import chat, interfaces

SESSION_KEY = 'z3c.formjsdemo.chat'

ChatCSSViewlet = CSSViewlet('chat.css')
ChatJSViewlet = JavaScriptViewlet('chat.js')


class SessionProperty(object):

    def __init__(self, name, default=None):
        self.name = name
        self.default = default

    def __get__(self, inst, klass):
        session = ISession(inst.request)[SESSION_KEY]
        return session.get(self.name, self.default)

    def __set__(self, inst, value):
        session = ISession(inst.request)[SESSION_KEY]
        session[self.name] = value


class ChatRoomAddForm(layout.FormLayoutSupport, form.AddForm):

    label = "Add a Chat Room"
    fields = field.Fields(interfaces.IChatRoom).select('topic')

    def create(self, data):
        return chat.ChatRoom(data['topic'])

    def add(self, object):
        name = object.topic.lower().replace(' ','')
        context = removeSecurityProxy(self.context)
        name = INameChooser(context).chooseName(name, object)
        context[name] = object
        self._name = name

    def nextURL(self):
        return absoluteURL(removeSecurityProxy(self.context)[self._name], self.request)


class IButtons(zope.interface.Interface):
    send = jsaction.JSButton(title=u'Send')
    connect = jsaction.JSButton(title=u'Connect')

class IFields(zope.interface.Interface):
    message = zope.schema.TextLine(title=u"Message")
    nick = zope.schema.TextLine(title=u"Nick")

class ChatForm(layout.FormLayoutSupport,
               ajax.AJAXRequestHandler,
               form.Form):
    buttons = button.Buttons(IButtons)
    fields = field.Fields(IFields)

    nick = SessionProperty('nick')

    @jsaction.handler(buttons['connect'])
    def handleConnect(self, event, selecter):
        nickId = self.widgets['nick'].id
        messageId = self.widgets['message'].id
        return '''$.get("@@index.html/@@ajax/joinChat", {nick: $("#%s").val()}, function(data){
                                $("#%s").attr("disabled", "true");
                                $("#connect").addClass("translucent");
                                $("#online").removeClass("translucent");
                                $("#%s").removeAttr("disabled");
                             });
                             ''' % (nickId, nickId, messageId)

    def _send(self, messageId):
        return '''$.get("@@index.html/@@ajax/addMessage", {message: $("#%s").val()},
                        function(data){
                            $("#%s").val("");
                        }
                       );''' % (messageId, messageId)

    @jsaction.handler(fields['message'], event=jsevent.KEYDOWN)
    def handleMessageEnter(self, event, selecter):
        return '''if (event.which != 13){ return null; }
                  %s''' % self._send(self.widgets['message'].id)

    @jsaction.handler(buttons['send'])
    def handleSend(self, event, selecter):
        return self._send(self.widgets['message'].id)

    def updateWidgets(self):
        '''See interfaces.IForm'''
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        self.widgets.ignoreContext = True
        self.widgets.update()

    @ajax.handler
    def getMessages(self):
        index = int(self.request.get('index'))
        result = ""
        for nick, message in self.context.messages[index:]:
            result += self._renderMessage(nick, message)
        return result

    @ajax.handler
    def addMessage(self):
        message = self.request.get('message')
        if message is not None:
            self.context.addMessage(self.nick, message)
        return self._renderMessage(self.nick, message)

    @ajax.handler
    def joinChat(self):
        self.nick = self.request.get('nick', 'anonymous')
        return "Connected as %s" % self.nick


    def _renderMessage(self, nick, message):
        return '<div class="message"><span class="nick">%s:</span>%s</div>' % (
            nick, message)
