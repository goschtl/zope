##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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

"""Vocabulary widget support.

This includes support for vocabulary fields' use of the vocabulary to
determine the actual widget to display, and support for supplemental
query objects and helper views.

"""

from xml.sax.saxutils import quoteattr

from zope.app.browser.form import widget
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.interfaces.browser.form import IVocabularyQueryView
from zope.publisher.browser import BrowserView
from zope.component import getView
from zope.schema.interfaces import IIterableVocabulary, IVocabularyQuery
from zope.schema.interfaces import IIterableVocabularyQuery


# These widget factories delegate to the vocabulary on the field.

def VocabularyFieldDisplayWidget(field, request):
    """Return a display widget based on a vocabulary field."""
    return _get_vocabulary_widget(field, request, "display")

def VocabularyFieldEditWidget(field, request):
    """Return a value-selection widget based on a vocabulary field."""
    return _get_vocabulary_edit_widget(field, request, ismulti=False)

def VocabularyMultiFieldDisplayWidget(field, request):
    """Return a display widget based on a vocabulary field."""
    return _get_vocabulary_widget(field, request, "display-multi")

def VocabularyMultiFieldEditWidget(field, request):
    """Return a value-selection widget based on a vocabulary field."""
    return _get_vocabulary_edit_widget(field, request, ismulti=True)


# Helper functions for the factories:

def _get_vocabulary_widget(field, request, viewname):
    view = getView(field.vocabulary, "field-%s-widget" % viewname, request)
    view.setField(field)
    return view

def _get_vocabulary_edit_widget(field, request, ismulti):
    if ismulti:
        viewname = "edit-multi"
        queryname = "widget-query-multi-helper"
    else:
        viewname = "edit"
        queryname = "widget-query-helper"
    view = _get_vocabulary_widget(field, request, viewname)
    query = field.vocabulary.getQuery()
    if query is None and IIterableVocabulary.isImplementedBy(field.vocabulary):
        query = IterableVocabularyQuery(field.vocabulary)
    if query is not None:
        queryview = getView(query, queryname, request)
        view.setQuery(query, queryview)
    return view


class IterableVocabularyQuery:
    """Simple query object used to invoke the simple selection mechanism."""

    __implements__ = IIterableVocabularyQuery

    def __init__(self, vocabulary):
        self.vocabulary = vocabulary


# Widget implementation:

class ViewSupport:
    """Helper class for vocabulary and vocabulary-query widgets."""

    def textForValue(self, term):
        # Extract the value from the term.  This can be overridden to
        # support more complex term objects.
        return term.value

    def mkselectionlist(self, type, info, name):
        L = ["<table>\n"]
        for term, selected, disabled in info:
            flag = ""
            if selected:
                flag = "checked "
            if disabled:
                flag += "disabled "
            L.append("<tr><td>"
                     "<input type='%s' value='%s' name='%s' %s/>"
                     "</td>\n    <td>%s</td>"
                     "</tr>\n"
                     % (type, term.value, name, flag, self.textForValue(term)))
        L.append("</table>")
        return ''.join(L)


class VocabularyWidgetBase(ViewSupport, widget.BrowserWidget):
    """Convenience base class for vocabulary-based widgets."""

    propertyNames = widget.BrowserWidget.propertyNames + ["extra"]

    extra = ""
    type = "vocabulary"

    def __init__(self, context, request):
        self.request = request
        self.context = None

    def _getDefault(self):
        # Override this since the context is not the field for
        # vocabulary-based widgets.
        return self.context.default

    def setField(self, field):
        assert self.context is None
        # only allow this to happen for a bound field
        assert field.context is not None
        self.context = field
        self.name = self._prefix + field.__name__

    def __call__(self):
        if self.haveData():
            value = self._showData()
        else:
            value = self.context.get(self.context.context)
        return self.render(value)

    def render(self, value):
        raise NotImplementedError(
            "render() must be implemented by a subclass")


class VocabularyDisplayWidget(VocabularyWidgetBase):
    """Simple single-selection display that can be used in many cases."""

    def render(self, value):
        term = self.context.vocabulary.getTerm(value)
        return self.textForValue(term)


class VocabularyMultiDisplayWidget(VocabularyWidgetBase):

    propertyNames = (VocabularyWidgetBase.propertyNames
                     + ['itemTag', 'tag'])

    itemTag = 'li'
    tag = 'ol'

    def render(self, value):
        if value == self._missing:
            return widget.renderElement('span',
                                        type=self.getValue('type'),
                                        name=self.name,
                                        id=self.name,
                                        cssClass=self.getValue('cssClass'),
                                        contents=_("(no values)"),
                                        extra=self.getValue('extra'))
        else:
            rendered_items = self.renderItems(value)
            return widget.renderElement(self.getValue('tag'),
                                        type=self.getValue('type'),
                                        name=self.name,
                                        id=self.name,
                                        cssClass=self.getValue('cssClass'),
                                        contents="\n".join(rendered_items),
                                        extra=self.getValue('extra'))

    def renderItems(self, value):
        L = []
        vocabulary = self.context.vocabulary
        cssClass = self.getValue('cssClass') or ''
        if cssClass:
            cssClass += "-item"
        tag = self.getValue('itemTag')
        for v in value:
            term = vocabulary.getTerm(v)
            L.append(widget.renderElement(tag,
                                          cssClass=cssClass,
                                          contents=self.textForValue(term)))
        return L


class VocabularyEditWidgetBase(VocabularyWidgetBase):
    propertyNames = (VocabularyWidgetBase.propertyNames
                     + ['size', 'tag'])
    size = 5
    tag = 'select'

    query = None
    queryview = None

    def setQuery(self, query, queryview):
        assert self.query is None
        assert self.queryview is None
        if query is None:
            assert queryview is None
        else:
            assert queryview is not None
            self.query = query
            self.queryview = queryview
            # Use of a hyphen to form the name for the query widget
            # ensures that it won't clash with anything else, since
            # field names are normally Python identifiers.
            queryview.setName(self.name + "-query")

    def setPrefix(self, prefix):
        VocabularyWidgetBase.setPrefix(self, prefix)
        if self.queryview is not None:
            self.queryview.setName(self.name + "-query")

    def render(self, value):
        contents = []
        have_results = False
        if self.queryview:
            s = self.queryview.renderResults(value)
            if s:
                contents.append(self._div('queryresults', s))
                s = self.queryview.renderInput()
                contents.append(self._div('queryinput', s))
                have_results = True
        contents.append(self._div('value', self.renderValue(value)))
        if self.queryview and not have_results:
            s = self.queryview.renderInput()
            if s:
                contents.append(self._div('queryinput', s))
        return self._div(self.getValue('cssClass'), "\n".join(contents),
                         id=self.name,
                         extra=self.getValue('extra'))

    def _div(self, cssClass, contents, **kw):
        if contents:
            return widget.renderElement('div',
                                        cssClass=cssClass,
                                        contents="\n%s\n" % contents,
                                        **kw)
        return ""

    def renderItemsWithValues(self, values):
        """Render the list of possible values, with those found in
        'values' being marked as selected."""

        cssClass = self.getValue('cssClass')

        # multiple items with the same value are not allowed from a
        # vocabulary, so that need not be considered here
        rendered_items = []
        count = 0
        for term in self.context.vocabulary:
            item_value = term.value
            item_text = self.textForValue(term)

            if item_value in values:
                rendered_item = self.renderSelectedItem(count,
                                                        item_text,
                                                        item_value,
                                                        self.name,
                                                        cssClass)
            else:
                rendered_item = self.renderItem(count,
                                                item_text,
                                                item_value,
                                                self.name,
                                                cssClass)

            rendered_items.append(rendered_item)
            count += 1

        return rendered_items

    def renderItem(self, index, text, value, name, cssClass):
        return widget.renderElement('option',
                                    contents=text,
                                    value=value,
                                    cssClass=cssClass)

    def renderSelectedItem(self, index, text, value, name, cssClass):
        return widget.renderElement('option',
                                    contents=text,
                                    value=value,
                                    cssClass=cssClass,
                                    selected=None)


class VocabularyEditWidget(VocabularyEditWidgetBase):
    """Vocabulary-backed single-selection edit widget.

    This widget can be used when the number of selections isn't going
    to be very large.
    """
    __implements__ = widget.SingleItemsWidget.__implements__
    propertyNames = VocabularyEditWidgetBase.propertyNames + ['firstItem']
    firstItem = False

    def renderValue(self, value):
        rendered_items = self.renderItems(value)
        contents = "\n%s\n" % "\n".join(rendered_items)
        return widget.renderElement('select',
                                    name=self.name,
                                    contents=contents,
                                    size=self.getValue('size'))

    def renderItems(self, value):
        vocabulary = self.context

        # check if we want to select first item
        if (value == self._missing
            and getattr(self.context, 'firstItem', False)
            and len(vocabulary) > 0):
            # Grab the first item from the iterator:
            values = [iter(vocabulary).next().value]
        elif value != self._missing:
            values = [value]
        else:
            values = ()

        return VocabularyEditWidgetBase.renderItemsWithValues(self, values)

    def hidden(self):
        return widget.renderElement('input',
                                    type='hidden',
                                    name=self.name,
                                    id=self.name,
                                    value=self._showData())


class VocabularyMultiEditWidget(VocabularyEditWidgetBase):
    """Vocabulary-backed widget supporting multiple selections."""

    def renderItems(self, value):
        if value == self._missing:
            values = ()
        else:
            values = list(value)
        return VocabularyEditWidgetBase.renderItemsWithValues(self, values)

    def renderValue(self, value):
        # All we really add here is the ':list' in the name argument
        # to widget.renderElement().
        rendered_items = self.renderItems(value)
        return widget.renderElement(self.getValue('tag'),
                                    name=self.name + ':list',
                                    multiple=None,
                                    size=self.getValue('size'),
                                    contents="\n".join(rendered_items))

    def hidden(self):
        L = []
        for v in self._showData():
            s = widget.renderElement('input',
                                     type='hidden',
                                     name=self.name + ':list',
                                     value=v)
            assert s[-1] == '>'
            L.append(s[:-1])
            L.append('\n>')
        return ''.join(L)


class VocabularyQueryViewBase(ViewSupport, BrowserView):
    """Vocabulary query support base class."""

    __implements__ = IVocabularyQueryView

    # This specifically isn't a widget in it's own right, but is a
    # form of BrowserView (at least conceptually).

    def __init__(self, context, request):
        self.vocabulary = context.vocabulary
        self.context = context
        self.request = request
        super(VocabularyQueryViewBase, self).__init__(context, request)

    def setName(self, name):
        assert not name.endswith(".")
        self.name = name

    def renderInput(self):
        return self.renderQueryInput()

    def renderResults(self, value):
        results = self.getResults()
        if results is not None:
            return self.renderQueryResults(results, value)
        else:
            return ""

    def renderQueryResults(self, results, value):
        raise NotImplementedError(
            "renderQueryResults() must be implemented by a subclass")

    def renderQueryInput(self):
        raise NotImplementedError(
            "renderQueryInput() must be implemented by a subclass")

    def getResults(self):
        # This is responsible for running the query against the query
        # object (self.context), and returning a results object.  If
        # there isn't a query in the form, returns None.
        return None

    _performed_action = False

    def performAction(self, value):
        """Make sure the real action, performQueryAction(), only runs once."""
        if self._performed_action:
            return value
        self._performed_action = True
        return self.performQueryAction(value)


ADD_DONE = "adddone"
ADD_MORE = "addmore"
MORE = "more"

def _message(msgid, default):
    msgid.default = default
    return msgid


class IterableVocabularyQueryViewBase(VocabularyQueryViewBase):
    """Query view for IIterableVocabulary objects without more
    specific query views.

    This should only be used (directly) for vocabularies for which
    getQuery() returns None.
    """

    __implements__ = IVocabularyQueryView

    queryResultBatchSize = 8

    action = None

    def setName(self, name):
        VocabularyQueryViewBase.setName(self, name)
        name = self.name
        self.adddone_name = name + "." + ADD_DONE
        self.addmore_name = name + "." + ADD_MORE
        self.more_name = name + "." + MORE
        self.query_index_name = name + ".start"
        self.query_selections_name = name + ".picks"
        #
        get = self.request.form.get
        if get(self.adddone_name):
            self.action = ADD_DONE
        elif get(self.addmore_name):
            self.action = ADD_MORE
        elif get(self.more_name):
            self.action = MORE
        try:
            self.query_index = int(get(self.query_index_name, 0))
        except ValueError:
            self.query_index = 0
        else:
            if self.query_index < 0:
                self.query_index = 0
        self.query_selections = get(self.query_selections_name, [])
        if not isinstance(self.query_selections, list):
            self.query_selections = [self.query_selections]

    def renderQueryInput(self):
        # There's no query support, so we can't actually have input.
        return ""

    def getResults(self):
        return self.vocabulary

    def renderQueryResults(self, results, value):
        # display query results batch
        it = iter(results)
        qi = self.query_index
        have_more = True
        try:
            for xxx in range(qi):
                it.next()
        except StopIteration:
            have_more = False
        items = []
        QS = []
        try:
            for i in range(qi, qi + self.queryResultBatchSize):
                term = it.next()
                disabled = term.value in value
                selected = disabled
                if term.value in self.query_selections:
                    QS.append(term.value)
                    selected = True
                items.append((term, selected, disabled))
            else:
                # see if there's anything else:
                it.next()
        except StopIteration:
            have_more = False
        self.query_selections = QS
        L = ["<div class='results'>\n",
             self.makeSelectionList(items, self.query_selections_name),
             "\n",
             self._mkbutton(ADD_DONE), "\n",
             self._mkbutton(ADD_MORE, not have_more), "\n",
             self._mkbutton(MORE, not have_more), "\n"]
        if qi:
            L.append("<input type='hidden' name='%s' value='%d' />\n"
                     % (self.query_index_name, qi))
        L.append("</div>")
        return ''.join(L)

    _messages = {
        ADD_DONE: _message(_("vocabulary-query-button-add-done"), "Add"),
        ADD_MORE: _message(_("vocabulary-query-button-add-more"), "Add+More"),
        MORE:     _message(_("vocabulary-query-button-more"),     "More"),
        }

    def _mkbutton(self, action, disabled=False):
        msg = self._messages[action]
        return ("<input name='%s.%s' type='submit' value=%s %s/>"
                % (self.name, action,
                   quoteattr(self.translate(msg)),
                   (disabled and "disabled " or "")))

    def translate(self, msgid):
        # XXX This is where we should be calling on the translation service
        return msgid.default

    def performQueryAction(self, value):
        if self.action == ADD_DONE:
            value = self.addSelections(value)
            self.query_index = 0
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
            if item not in value and item in self.context.vocabulary:
                value.append(item)
        return value

class IterableVocabularyQueryView(IterableVocabularyQueryViewBase):

    def makeSelectionList(self, items, name):
        return self.mkselectionlist("radio", items, name)

    def renderQueryResults(self, results, value):
        return IterableVocabularyQueryViewBase.renderQueryResults(
            self, results, [value])

class IterableVocabularyQueryMultiView(IterableVocabularyQueryViewBase):

    def makeSelectionList(self, items, name):
        return self.mkselectionlist("checkbox", items, name)
