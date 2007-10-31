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
from zope.interface import Interface, implements
from zope.security.proxy import removeSecurityProxy
from zope.app.container.interfaces import INameChooser
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.viewlet.viewlet import CSSViewlet
from zope.component import getMultiAdapter
from zope.viewlet.viewlet import JavaScriptViewlet
from zope.publisher.interfaces.browser import IBrowserPage
from zope.component import getMultiAdapter
from zope.publisher.interfaces import IPublishTraverse
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.component.interfaces import IObjectEvent
from zope.app.container.interfaces import IObjectAddedEvent
from zope.session.interfaces import ISession

from z3c.form import form, field, button
from z3c.formui import layout
from z3c.form.interfaces import IWidgets, DISPLAY_MODE

from z3c.formjs import jsaction, jsfunction, jsclientevent, ajax
from z3c.formjs.interfaces import IJSButton
import tree, interfaces

TreeCSSViewlet = CSSViewlet('tree.css')
JQueryFormPluginViewlet = JavaScriptViewlet('jquery.form.js')

SESSION_KEY = 'z3c.formjsdemo.tree'

class PrefixForm(object):

    postfix = ''

    @property
    def prefix(self):
        url = absoluteURL(self.context, self.request)
        return '-'.join((str(hash(url)), str(self.postfix)))


class EventsForm(jsclientevent.ClientEventsForm):

    @jsclientevent.listener((interfaces.ITreeNode, IObjectEvent))
    def updateEventList(self, event):
        info = repr(event).replace('<','&lt;').replace('>','&gt;').replace('"',"'")
        return '$("#server-events-container").append("<div>%s</div>")' % info


class TreeNodeInlineAddForm(PrefixForm, EventsForm, form.AddForm):
    """Form for adding a tree node.

    This page is meant to be inlined into another page.
    """
    label = "Add a Tree Node"
    fields = field.Fields(interfaces.ITreeNode).select('title')
    postfix = 'add'
    jsClientListeners = EventsForm.jsClientListeners

    @jsclientevent.listener((interfaces.ITreeNode, IObjectAddedEvent))
    def updateContents(self, event):
        indexForm = TreeNodeInlineForm(self.context, self.request)
        indexForm.update()
        expandId = indexForm.actions['expand'].id
        return '$("#%s").click()' % expandId

    def create(self, data):
        return tree.TreeNode(data['title'])

    def add(self, object):
        name = object.title.lower().replace(' ','')
        context = removeSecurityProxy(self.context)
        name = INameChooser(context).chooseName(name, object)
        context[name] = object
        self._name = name

    def render(self):
        """Custom render method that does not use nextURL method."""
        if self._finishedAdd:
            return '<script type="text/javascript">%s</script>' % self.eventInjections
        return super(TreeNodeInlineAddForm, self).render()


class TreeNodeAddForm(layout.FormLayoutSupport, TreeNodeInlineAddForm):
    """Stand Along version of the addform.

    This form is meant to appear on a page all by itself.
    """
    def nextURL(self):
        return absoluteURL(removeSecurityProxy(self.context)[self._name],
                           self.request)

    # this will use the nextURL method
    render = form.AddForm.render


class TreeNodeForm(PrefixForm, layout.FormLayoutSupport,
                   form.Form):

    postfix = 'main' # distinguish prefix from others on the page.
    fields = field.Fields(interfaces.ITreeNode).select('title')

    def updateWidgets(self):
        self.widgets = getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        self.widgets.mode = DISPLAY_MODE
        self.widgets.update()

    @jsfunction.function('tree')
    def expandNode(self, url, expanderId, contractorId, containerId):
        """Expand the node that using the given prefix and url"""
        return '''
        $.get(url,
          function(data){
            $("#"+expanderId).addClass("hidden");
            $("#"+contractorId).removeClass("hidden");
            $("#"+containerId).html(data);
          }
        );
        '''

    @jsfunction.function('tree')
    def contractNode(self, expanderId, contractorId, containerId):
        """Expand the node that using the given prefix and url"""
        return '''
        $("#"+expanderId).removeClass("hidden");
        $("#"+contractorId).addClass("hidden");
        $("#"+containerId).html('');
        '''

class IButtons(Interface):
    """Buttons for the inline tree node form."""

    expand = jsaction.JSButton(title=u'+')
    contract = jsaction.JSButton(title=u'-')


class TreeNodeInlineForm(PrefixForm, ajax.AJAXRequestHandler,
                         EventsForm, form.Form):

    fields = field.Fields(interfaces.ITreeNode).select('title')
    buttons = button.Buttons(IButtons)
    jsClientListeners = EventsForm.jsClientListeners

    @jsaction.handler(buttons['expand'])
    def handleExpand(self, event, selector):
        url = absoluteURL(self.context, self.request) + '/@@contents'
        call = TreeNodeForm.expandNode.call(url,
                                            self.actions['expand'].id,
                                            self.actions['contract'].id,
                                            self.prefix+'-inlinecontent')
        path = absoluteURL(self.context, self.request)
        store = '$.get("%s/@@inline/@@ajax/storeExpand", function(data){});' % path
        return '\n'.join((call, store))

    @jsaction.handler(buttons['contract'])
    def handleContract(self, event, selector):
        call = TreeNodeForm.contractNode.call(self.actions['expand'].id,
                                              self.actions['contract'].id,
                                              self.prefix+'-inlinecontent')
        path = absoluteURL(self.context, self.request)
        store = '$.get("%s/@@inline/@@ajax/storeContract", function(data){});' % path
        return '\n'.join((call, store))

    @ajax.handler
    def storeExpand(self):
        self._setExpanded(True)
        return "success"

    @ajax.handler
    def storeContract(self):
        self._setExpanded(False)
        return "success"

    def _setExpanded(self, value):
        session = ISession(self.request)[SESSION_KEY]
        session[self.prefix + '-expanded'] = value

    @property
    def expanded(self):
        session = ISession(self.request)[SESSION_KEY]
        return session.get(self.prefix+'-expanded', False)

    def updateActions(self):
        super(TreeNodeInlineForm, self).updateActions()
        if self.expanded:
            self.actions['expand'].addClass('hidden')
        else:
            self.actions['contract'].addClass('hidden')

    def updateWidgets(self):
        self.widgets = getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        self.widgets.mode = DISPLAY_MODE
        self.widgets.update()


class TreeNodeInlineEditForm(PrefixForm, EventsForm, form.EditForm):

    fields = field.Fields(interfaces.ITreeNode).select('title')
    jsClientListeners = EventsForm.jsClientListeners

    _applyChangesWasCalled = False

    def applyChanges(self, data):
        self._applyChangesWasCalled = True
        return super(TreeNodeInlineEditForm, self).applyChanges(data)

    @jsclientevent.listener((interfaces.ITreeNode, IObjectModifiedEvent))
    def updateTitle(self, event):
        inlineform = TreeNodeInlineForm(self.context, self.request)
        inlineform.update()
        titleId = inlineform.widgets['title'].id
        mainform = TreeNodeForm(self.context, self.request)
        mainform.update()
        mainTitleId = mainform.widgets['title'].id
        lines = ['$("#%s").html("%s")' % (titleId, self.context.title),
                 '$("#%s").html("%s")' % (mainTitleId, self.context.title)]
        return '\n'.join(lines)

    def render(self):
        if self._applyChangesWasCalled:
            return '<script type="text/javascript">%s</script>' % self.eventInjections
        else:
            return super(TreeNodeInlineEditForm, self).render()

class IInlineFormButton(IJSButton):
    """A button that points to an inline form."""


class InlineFormButton(jsaction.JSButton):
    """implementer of IInlineFormButton"""
    implements(IInlineFormButton)


class IContentButtons(Interface):
    """Buttons for the inline contents view."""

    add = InlineFormButton(title=u'Add')
    edit = InlineFormButton(title=u'Edit')


class TreeNodeInlineContentsForm(PrefixForm, form.Form):

    postfix = 'contents'

    buttons = button.Buttons(IContentButtons)

    def _handleInlineFormButton(self, viewURL):
        return '''$.get("%s",
                      function(data){
                          $("#%s-inlineform").html(data);
                          $("#%s-inlineform form").ajaxForm(
                              function(data){
                                  $("body").append(data);
                              });
                  });
               ''' % (viewURL, self.prefix, self.prefix)

    @jsaction.handler(buttons['add'])
    def handleAdd(self, event, selector):
        viewURL = absoluteURL(self.context, self.request) + '/@@add'
        return self._handleInlineFormButton(viewURL)

    @jsaction.handler(buttons['edit'])
    def handleEdit(self, event, selector):
        viewURL = absoluteURL(self.context, self.request) + '/@@edit'
        return self._handleInlineFormButton(viewURL)
