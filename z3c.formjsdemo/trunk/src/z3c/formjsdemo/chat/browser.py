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
from z3c.form import form, button, field
from z3c.form.interfaces import IWidgets
from z3c.formui import layout
from z3c.formjs import jsaction, jsevent

from z3c.formjsdemo.chat import chat, interfaces

ChatCSSViewlet = CSSViewlet('chat.css')
ChatJSViewlet = JavaScriptViewlet('chat.js')

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

class IFields(zope.interface.Interface):
    message = zope.schema.TextLine(title=u"Message")

class ChatForm(layout.FormLayoutSupport, form.Form):
    buttons = button.Buttons(IButtons)
    fields = field.Fields(IFields)

    @jsaction.handler(buttons['send'])
    def handleSend(self, selecter):
        messageId = self.widgets['message'].id
        return '''$.get("addMessage", {message: $("#%s").val()}, function(data){
                                $("#%s").val("");
                             });
                             ''' % (messageId, messageId)

    def updateWidgets(self):
        '''See interfaces.IForm'''
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        self.widgets.ignoreContext = True
        self.widgets.update()


def renderMessage(message):
    return '<div class="message">%s</div>' % message


class AddMessageView(object):

    def __call__(self):
        message = self.request.get('message')
        if message is not None:
            self.context.addMessage(message)
        return renderMessage(message)


class GetMessagesView(object):

    def __call__(self):
        index = int(self.request.get('index'))
        result = ""
        for message in self.context.messages[index:]:
            result += renderMessage(message)
        return result
