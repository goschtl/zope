##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Browser views for vocabulary widgets.

$Id: vocabularyquery.py,v 1.1 2004/04/24 23:18:16 srichter Exp $
"""
from zope.interface import implements
from zope.schema.interfaces import IIterableVocabularyQuery

from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.publisher.browser import BrowserView

from zope.app.form.browser.itemswidgets import TranslationHook, message
from zope.app.form.browser.interfaces import IVocabularyQueryView
from zope.app.form.browser.widget import renderElement

ADD_DONE = u"adddone"
ADD_MORE = u"addmore"
MORE = u"more"


class ActionHelper(TranslationHook):
    """Helper class to allow sub-actions for a particular widget.

    It is used to execute queries on a large set of vocabulary terms. Note
    that a vocabulary has to support queries for this."""
    __actions = None

    def addAction(self, action, msgid):
        """Add an action for the widget."""
        if self.__actions is None:
            self.__actions = {}
        assert action not in self.__actions
        self.__actions[action] = msgid

    def getAction(self):
        """Retrieve a the executed action from the form.

        Return None, if none of the registered actions was called.
        """
        assert self.__actions is not None, \
               "getAction() called on %r with no actions defined" %self
        for action in self.__actions.iterkeys():
            name = "%s.action-%s" % (self.name, action)
            if self.request.form.get(name):
                return action
        return None

    def renderAction(self, action, disabled=False):
        """Render a particular action as a HTML submit button."""
        msgid = self.__actions[action]
        return ('<input type="submit" name="%s.action-%s" value=%s %s />'
                % (self.name, action, quoteattr(self.translate(msgid)),
                   disabled and 'disabled="disabled"' or ""))


class ViewSupport(TranslationHook):
    """Helper class for vocabulary query views.

    This is mixed into the query view base class.
    """

    def textForValue(self, term):
        """Extract a string from the term.

        The term must be a vocabulary tokenized term. 

        This can be overridden to support more complex term objects. The token
        is returned here since it's the only thing known to be a string, or
        str()able."""
        return term.token

    def mkselectionlist(self, type, info, name):
        """Create a list of selections."""
        items = [self.mkselectionitem(type, name, *item) for item in info]
        return renderElement("table",
                             contents="\n%s\n" % "\n".join(items))

    def mkselectionitem(self, type, name, term, selected, disabled):
        """Create a single secetion item."""
        flag = ''
        if selected:
            flag = ' checked="checked"'
        if disabled:
            flag += ' disabled="disabled"'
        if flag:
            flag = "\n      " + flag
        return ('<tr><td>'
                '<input type="%s" value="%s" name="%s"%s />'
                '</td>\n    <td>%s</td></tr>'
                % (type, term.token, name, flag, self.textForValue(term)))


class VocabularyQueryViewBase(ActionHelper, ViewSupport, BrowserView):
    """Vocabulary query support base class."""
    implements(IVocabularyQueryView)

    def __init__(self, query, field, request):
        super(VocabularyQueryViewBase, self).__init__(query, request)
        self.vocabulary = query.vocabulary
        self.field = field
        self.widget = None

    def setName(self, name):
        """See interfaces.IVocabularyQueryView"""
        assert not name.endswith(".")
        self.name = name

    def setWidget(self, widget):
        assert self.widget is None
        assert widget is not None
        self.widget = widget

    def performAction(self, value):
        """See interfaces.IVocabularyQueryView"""
        return value

    def renderInput(self):
        """See interfaces.IVocabularyQueryView"""
        return self._renderQueryInput()

    def renderResults(self, value):
        """See interfaces.IVocabularyQueryView"""
        results = self._getResults()
        if results is not None:
            return self._renderQueryResults(results, value)
        else:
            return ""

    def _renderQueryResults(self, results, value):
        raise NotImplementedError(
            "_renderQueryResults() must be implemented by a subclass")

    def _renderQueryInput(self):
        raise NotImplementedError(
            "_renderQueryInput() must be implemented by a subclass")

    def _getResults(self):
        # This is responsible for running the query against the query
        # object (self.context), and returning a results object.  If
        # there isn't a query in the form, returns None.
        return None


class IterableVocabularyQueryViewBase(VocabularyQueryViewBase):
    """Query view for IIterableVocabulary objects without more
    specific query views.

    This should only be used (directly) for vocabularies for which
    getQuery() returns None.
    """
    queryResultBatchSize = 8

    _msg_add_done = message(_("vocabulary-query-button-add-done"),
                            "Add+Done")
    _msg_add_more = message(_("vocabulary-query-button-add-more"),
                            "Add+More")
    _msg_more = message(_("vocabulary-query-button-more"),
                        "More")
    _msg_no_results = message(_("vocabulary-query-message-no-results"),
                              "No Results")
    _msg_results_header = message(_("vocabulary-query-header-results"),
                                 "Search results")

    def __init__(self, *args, **kw):
        super(IterableVocabularyQueryViewBase, self).__init__(*args, **kw)
        self.addAction(ADD_DONE, self._msg_add_done)
        self.addAction(ADD_MORE, self._msg_add_more)
        self.addAction(MORE,     self._msg_more)

    def setName(self, name):
        """See interfaces.IVocabularyQueryView"""
        super(IterableVocabularyQueryViewBase, self).setName(name)
        name = self.name
        self.query_index_name = name + ".start"
        self.query_selections_name = name + ".picks"
        #
        get = self.request.form.get
        self.action = self.getAction()
        self.query_index = None
        if self.query_index_name in self.request.form:
            try:
                index = int(self.request.form[self.query_index_name])
            except ValueError:
                pass
            else:
                if index >= 0:
                    self.query_index = index
        querySelections = get(self.query_selections_name, [])
        if not isinstance(querySelections, list):
            querySelections = [querySelections]
        self.query_selections = []
        for token in querySelections:
            try:
                term = self.vocabulary.getTermByToken(token)
            except LookupError:
                # XXX unsure what to pass to exception constructor
                raise WidgetInputError(
                    "(query view for %s)" % self.context,
                    "(query view for %s)" % self.context,
                    "token %r not in vocabulary" % token)
            else:
                self.query_selections.append(term.value)

    def _renderQueryInput(self):
        # There's no query support, so we can't actually have input.
        return ""

    def _getResults(self):
        if self.query_index is not None:
            return self.vocabulary
        else:
            return None

    def _renderQueryResults(self, results, value):
        # display query results batch
        it = iter(results)
        qi = self.query_index
        have_more = True
        try:
            for xxx in range(qi):
                it.next()
        except StopIteration:
            # we should only get here with a botched request; ADD_MORE
            # and MORE will normally be disabled if there are no results
            # (see below)
            have_more = False
        items = []
        querySelections = []
        try:
            for i in range(qi, qi + self.queryResultBatchSize):
                term = it.next()
                disabled = term.value in value
                selected = disabled
                if term.value in self.query_selections:
                    querySelections.append(term.value)
                    selected = True
                items.append((term, selected, disabled))
            else:
                # see if there's anything else:
                it.next()
        except StopIteration:
            if not items:
                return "<div class='results'>%s</div>" % (
                    self.translate(self._msg_no_results))
            have_more = False
        self.query_selections = querySelections
        return ''.join(
            ["<div class='results'>\n",
             "<h4>%s</h4>\n" % (
                 self.translate(self._msg_results_header)),
             self.makeSelectionList(items, self.query_selections_name),
             "\n",
             self.renderAction(ADD_DONE), "\n",
             self.renderAction(ADD_MORE, not have_more), "\n",
             self.renderAction(MORE, not have_more), "\n"
             "<input type='hidden' name='%s' value='%d' />\n"
             % (self.query_index_name, qi),
             "</div>"])

    def performAction(self, value):
        """See interfaces.IVocabularyQueryView"""
        if self.action == ADD_DONE:
            value = self.addSelections(value)
            self.query_index = None
            self.query_selections = []
        elif self.action == ADD_MORE:
            value = self.addSelections(value)
            self.query_index += self.queryResultBatchSize
        elif self.action == MORE:
            self.query_index += self.queryResultBatchSize
        elif self.action:
            raise ValueError("unknown action in request: %r" % self.action)
        return value

    def addSelections(self, value):
        for item in self.query_selections:
            if item not in value and item in self.vocabulary:
                value.append(item)
        return value


class IterableVocabularyQueryView(IterableVocabularyQueryViewBase):

    def makeSelectionList(self, items, name):
        return self.mkselectionlist("radio", items, name)

    def _renderQueryResults(self, results, value):
        return super(IterableVocabularyQueryView, self)._renderQueryResults(
            results, [value])


class IterableVocabularyQueryMultiView(IterableVocabularyQueryViewBase):

    def makeSelectionList(self, items, name):
        return self.mkselectionlist("checkbox", items, name)
