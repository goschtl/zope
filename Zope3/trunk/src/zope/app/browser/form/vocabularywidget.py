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

from zope.interface import implements, implementedBy
from zope.app.browser.form import widget
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.interfaces.browser.form import IVocabularyQueryView
from zope.app.interfaces.form import WidgetInputError, MissingInputError
from zope.interface.declarations import directlyProvides
from zope.publisher.browser import BrowserView
from zope.component import getView
from zope.schema.interfaces import IIterableVocabulary, IVocabularyQuery
from zope.schema.interfaces import IIterableVocabularyQuery
from zope.schema.interfaces import ValidationError


# These widget factories delegate to the vocabulary on the field.

# Display

def VocabularyFieldDisplayWidget(field, request):
    """Return a display widget based on a vocabulary field."""
    return _get_vocabulary_widget(field, request, "display")

def VocabularyBagFieldDisplayWidget(field, request):
    """Return a display widget based on a vocabulary field."""
    return _get_vocabulary_widget(field, request, "display-bag")

def VocabularyListFieldDisplayWidget(field, request):
    """Return a display widget based on a vocabulary field."""
    return _get_vocabulary_widget(field, request, "display-list")

def VocabularySetFieldDisplayWidget(field, request):
    """Return a display widget based on a vocabulary field."""
    return _get_vocabulary_widget(field, request, "display-set")

def VocabularyUniqueListFieldDisplayWidget(field, request):
    """Return a display widget based on a vocabulary field."""
    return _get_vocabulary_widget(field, request, "display-unique-list")

# Edit

def VocabularyFieldEditWidget(field, request):
    """Return a value-selection widget based on a vocabulary field."""
    return _get_vocabulary_edit_widget(field, request)

def VocabularyBagFieldEditWidget(field, request):
    """Return a value-selection widget based on a vocabulary field."""
    return _get_vocabulary_edit_widget(field, request, "bag")

def VocabularyListFieldEditWidget(field, request):
    """Return a value-selection widget based on a vocabulary field."""
    return _get_vocabulary_edit_widget(field, request, "list")

def VocabularySetFieldEditWidget(field, request):
    """Return a value-selection widget based on a vocabulary field."""
    return _get_vocabulary_edit_widget(field, request, "set")

def VocabularyUniqueListFieldEditWidget(field, request):
    """Return a value-selection widget based on a vocabulary field."""
    return _get_vocabulary_edit_widget(field, request, "unique-list")


# Helper functions for the factories:

def _get_vocabulary_widget(field, request, viewname):
    view = getView(field.vocabulary, "field-%s-widget" % viewname, request)
    view.setField(field)
    return view

def _get_vocabulary_edit_widget(field, request, modifier=''):
    if modifier:
        modifier = "-" + modifier
    viewname = "edit" + modifier
    view = _get_vocabulary_widget(field, request, viewname)
    query = field.vocabulary.getQuery()
    if query is not None:
        queryname = "widget-query%s-helper" % modifier
        queryview = getView(query, queryname, request)
        view.setQuery(query, queryview)
    return view


class IterableVocabularyQuery(object):
    """Simple query object used to invoke the simple selection mechanism."""

    implements(IIterableVocabularyQuery)

    def __init__(self, vocabulary, *interfaces):
        self.vocabulary = vocabulary
        if interfaces:
            directlyProvides(self, *interfaces)


class TranslationHook:

    def translate(self, msgid):
        # XXX This is where we should be calling on the translation service
        return msgid.default

def message(msgid, default):
    msgid.default = default
    return msgid


# Widget implementation:

class ViewSupport(object, TranslationHook):
    """Helper class for vocabulary and vocabulary-query widgets."""

    def textForValue(self, term):
        # Extract a string from the term.  This can be overridden to
        # support more complex term objects.  The token is returned
        # here since it's the only thing known to be a string, or
        # str()able.
        return term.token

    def mkselectionlist(self, type, info, name):
        L = [self.mkselectionitem(type, name, *item) for item in info]
        return widget.renderElement("table",
                                    contents="\n%s\n" % "\n".join(L))

    def mkselectionitem(self, type, name, term, selected, disabled):
        flag = ""
        if selected:
            flag = " checked='checked'"
        if disabled:
            flag += " disabled='disabled'"
        if flag:
            flag = "\n      " + flag
        return ("<tr><td>"
                "<input type='%s' value='%s' name='%s'%s />"
                "</td>\n    <td>%s</td></tr>"
                % (type, term.token, name, flag, self.textForValue(term)))


class VocabularyWidgetBase(ViewSupport, widget.BrowserWidget):
    """Convenience base class for vocabulary-based widgets."""

    propertyNames = widget.BrowserWidget.propertyNames + ["extra"]

    extra = ""
    type = "vocabulary"
    context = None

    def __init__(self, context, request):
        self.request = request
        self.vocabulary = context
        # self.context is set to the field in setField below

    def setField(self, field):
        assert self.context is None
        # only allow this to happen for a bound field
        assert field.context is not None
        self.context = field
        self.setPrefix(self._prefix)
        assert self.name

    def setPrefix(self, prefix):
        super(VocabularyWidgetBase, self).setPrefix(prefix)
        # names for other information from the form
        self.empty_marker_name = self.name + "-empty-marker"

    def __call__(self):
        if self._data is None:
            if self.haveData():
                data = self.getData(True)
            else:
                data = self._getDefault()
        else:
            data = self._data
        return self.render(data)

    def render(self, value):
        raise NotImplementedError(
            "render() must be implemented by a subclass")

    def convertTokensToValues(self, tokens):
        L = []
        for token in tokens:
            try:
                term = self.context.vocabulary.getTermByToken(token)
            except LookupError:
                raise WidgetInputError(
                    self.context.__name__,
                    self.context.title,
                    "token %r not found in vocabulary" % token)
            else:
                L.append(term.value)
        return L

    _have_field_data = False

    def getData(self, optional=False):
        data = self._compute_data()
        field = self.context
        if data is None:
            if field.required and not optional:
                raise MissingInputError(field.__name__, field.title,
                                        'the field is required')
            return self._getDefault()
        elif not optional:
            try:
                field.validate(data)
            except ValidationError, v:
                raise WidgetInputError(self.context.__name__, self.title, v)
        return data

    def _emptyMarker(self):
        return "<input name='%s' type='hidden' value='1' />" % (
            self.empty_marker_name)

    def haveData(self):
        return (self.name in self.request.form or
                self.empty_marker_name in self.request.form)

    def setData(self, value):
        self._data = value

    def _compute_data(self):
        raise NotImplementedError(
            "_compute_data() must be implemented by a subclass\n"
            "It may be inherited from the mix-in classes SingleDataHelper\n"
            "or MultiDataHelper (from zope.app.browser.form.vocabularywidget)")

    def _showData(self):
        raise NotImplementedError(
            "vocabulary-based widgets don't use the _showData() method")

    def _convert(self, value):
        raise NotImplementedError(
            "vocabulary-based widgets don't use the _convert() method")

    def _unconvert(self, value):
        raise NotImplementedError(
            "vocabulary-based widgets don't use the _unconvert() method")

class SingleDataHelper(object):

    _msg_no_value = message(_("vocabulary-no-value"), "(no value)")

    def _compute_data(self):
        token = self.request.form.get(self.name)
        if token:
            return self.convertTokensToValues([token])[0]
        else:
            return None

class MultiDataHelper(object):

    def _compute_data(self):
        if self.name in self.request.form:
            tokens = self.request.form[self.name]
            if not isinstance(tokens, list):
                tokens = [tokens]
            return self.convertTokensToValues(tokens)
        return []

    def _getDefault(self):
        # Return the default value for this widget;
        # may be overridden by subclasses.
        val = self.context.default
        if val is None:
            val = []
        return val

class VocabularyDisplayWidget(SingleDataHelper, VocabularyWidgetBase):
    """Simple single-selection display that can be used in many cases."""

    def render(self, value):
        if value is None:
            return self.translate(self._msg_no_value)
        else:
            term = self.context.vocabulary.getTerm(value)
            return self.textForValue(term)


class VocabularyMultiDisplayWidget(MultiDataHelper, VocabularyWidgetBase):

    propertyNames = (VocabularyWidgetBase.propertyNames
                     + ['itemTag', 'tag'])

    itemTag = 'li'
    tag = 'ol'

    def render(self, value):
        if value:
            rendered_items = self.renderItems(value)
            return widget.renderElement(self.getValue('tag'),
                                        type=self.getValue('type'),
                                        name=self.name,
                                        id=self.name,
                                        cssClass=self.getValue('cssClass'),
                                        contents="\n".join(rendered_items),
                                        extra=self.getValue('extra'))
        else:
            return widget.renderElement('span',
                                        type=self.getValue('type'),
                                        name=self.name,
                                        id=self.name,
                                        cssClass=self.getValue('cssClass'),
                                        contents=_("(no values)"),
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


class VocabularyListDisplayWidget(VocabularyMultiDisplayWidget):
    """Display widget for ordered multi-selection fields.

    This can be used for both VocabularyListField and
    VocabularyUniqueListField fields.
    """
    tag = 'ol'


class VocabularyBagDisplayWidget(VocabularyMultiDisplayWidget):
    """Display widget for unordered multi-selection fields.

    This can be used for both VocabularyBagField and
    VocabularySetField fields.
    """
    tag = 'ul'


class ActionHelper(object, TranslationHook):
    __actions = None

    def addAction(self, action, msgid):
        if self.__actions is None:
            self.__actions = {}
        assert action not in self.__actions
        self.__actions[action] = msgid

    def getAction(self):
        assert self.__actions is not None, \
               "getAction() called on %r with no actions defined" % self
        get = self.request.form.get
        for action in self.__actions.iterkeys():
            name = "%s.action-%s" % (self.name, action)
            if get(name):
                return action
        return None

    def renderAction(self, action, disabled=False):
        msgid = self.__actions[action]
        return ("<input type='submit' name='%s.action-%s' value=%s %s/>"
                % (self.name, action, quoteattr(self.translate(msgid)),
                   disabled and "\n       disabled='disabled' " or ""))


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
        super(VocabularyEditWidgetBase, self).setPrefix(prefix)
        if self.queryview is not None:
            self.queryview.setName(self.name + "-query")

    def render(self, value):
        contents = []
        have_results = False
        if self.queryview is not None:
            s = self.queryview.renderResults(value)
            if s:
                contents.append(self._div('queryresults', s))
                s = self.queryview.renderInput()
                contents.append(self._div('queryinput', s))
                have_results = True
        contents.append(self._div('value', self.renderValue(value)))
        contents.append(self._emptyMarker())
        if self.queryview is not None and not have_results:
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
            item_text = self.textForValue(term)

            if term.value in values:
                rendered_item = self.renderSelectedItem(count,
                                                        item_text,
                                                        term.token,
                                                        self.name,
                                                        cssClass)
            else:
                rendered_item = self.renderItem(count,
                                                item_text,
                                                term.token,
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


class SelectListWidget(SingleDataHelper, VocabularyEditWidgetBase):
    """Vocabulary-backed single-selection edit widget.

    This widget can be used when the number of selections isn't going
    to be very large.
    """
    implements(implementedBy(widget.SingleItemsWidget))
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
        vocabulary = self.context.vocabulary
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
        L = self.renderItemsWithValues(values)
        if not self.context.required:
            option = ("<option name='%s' value=''>%s</option>"
                      % (self.name, self.translate(self._msg_no_value)))
            L.insert(0, option)
        return L

# more general alias
VocabularyEditWidget = SelectListWidget

class DropdownListWidget(SelectListWidget):
    """Variation of the SelectListWidget that uses a drop-down list."""

    size = 1

class VocabularyMultiEditWidget(MultiDataHelper, VocabularyEditWidgetBase):
    """Vocabulary-backed widget supporting multiple selections."""

    def renderItems(self, value):
        if value == self._missing:
            values = ()
        else:
            values = list(value)
        return self.renderItemsWithValues(values)

    def renderValue(self, value):
        # All we really add here is the ':list' in the name argument
        # to widget.renderElement().
        rendered_items = self.renderItems(value)
        return widget.renderElement(self.getValue('tag'),
                                    name=self.name + ':list',
                                    multiple=None,
                                    size=self.getValue('size'),
                                    contents="\n".join(rendered_items))


class VocabularyQueryViewBase(ActionHelper, ViewSupport, BrowserView):
    """Vocabulary query support base class."""

    implements(IVocabularyQueryView)

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

    def performAction(self, value):
        return value


ADD_DONE = "adddone"
ADD_MORE = "addmore"
MORE = "more"


class IterableVocabularyQueryViewBase(VocabularyQueryViewBase):
    """Query view for IIterableVocabulary objects without more
    specific query views.

    This should only be used (directly) for vocabularies for which
    getQuery() returns None.
    """

    implements(IVocabularyQueryView)

    queryResultBatchSize = 8

    _msg_add_done   = message(_("vocabulary-query-button-add-done"),
                              "Add+Done")
    _msg_add_more   = message(_("vocabulary-query-button-add-more"),
                              "Add+More")
    _msg_more       = message(_("vocabulary-query-button-more"),
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
        QS = get(self.query_selections_name, [])
        if not isinstance(QS, list):
            QS = [QS]
        self.query_selections = []
        for token in QS:
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

    def renderQueryInput(self):
        # There's no query support, so we can't actually have input.
        return ""

    def getResults(self):
        if self.query_index is not None:
            return self.vocabulary
        else:
            return None

    def renderQueryResults(self, results, value):
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
            if not items:
                return "<div class='results'>%s</div>" % (
                    self.translate(self._msg_no_results))
            have_more = False
        self.query_selections = QS
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
            if item not in value and item in self.context.vocabulary:
                value.append(item)
        return value

class IterableVocabularyQueryView(IterableVocabularyQueryViewBase):

    def makeSelectionList(self, items, name):
        return self.mkselectionlist("radio", items, name)

    def renderQueryResults(self, results, value):
        return super(IterableVocabularyQueryView, self).renderQueryResults(
            results, [value])

class IterableVocabularyQueryMultiView(IterableVocabularyQueryViewBase):

    def makeSelectionList(self, items, name):
        return self.mkselectionlist("checkbox", items, name)
