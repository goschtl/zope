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
"""Sample complex vocabulary widget with query support.

$Id$
"""
from xml.sax.saxutils import escape, quoteattr

from zope.app.form.browser.complexsample import widgetapi
from zope.app.form.browser.complexsample.widgetapi import _, message
from zope.app.form.browser.vocabularywidget import ActionHelper
from zope.app.form.interfaces import WidgetInputError
from zope.interface.declarations import implements
from zope.schema.interfaces import ITokenizedTerm


# values for the submit button:
MOVE_UP = "moveup"
MOVE_DOWN = "movedown"
REMOVE = "remove"

# value for the query helper submit button (other actions provided by
# base class):
ADD_DONE = "adddone"
ADD_MORE = "addmore"
MORE = "more"
CLEAR = "clear"
QUERY = "query"
SELECT = "select"
DISMISS = "dismiss"

# Message ids for actions that may make more sense to translators, or
# at least make it easier to isolate each bit of text in the widget:
_msg_moveup   = message(_("sampleWidget-button-move-up"),   "Move Up")
_msg_movedown = message(_("sampleWidget-button-move-down"), "Move Down")
_msg_remove   = message(_("sampleWidget-button-remove"),    "Remove")
_msg_add_done = message(_("sampleWidget-button-add-done"),  "Add+Done")
_msg_add_more = message(_("sampleWidget-button-add-more"),  "Add+More")
_msg_more     = message(_("sampleWidget-button-more"),      "More")
_msg_clear    = message(_("sampleWidget-button-clear"),     "Clear Value")
_msg_query    = message(_("sampleWidget-button-query"),     "Search")
_msg_select   = message(_("sampleWidget-button-select"),    "Select")
_msg_dismiss  = message(_("sampleWidget-button-dismiss"),   "Dismiss")
# Messages ids for labels in the widgets:
_msg_enter_search_text = message(
    _("sampleWidget-label-enter-search-text"), "Search for:")
_msg_select_content_type = message(
    _("sampleWidget-label-select-content-type"), "Select content type:")
_msg_any_content_type = message(
    _("sampleWidget-label-any-content-type"), "(any)")

_msg_inaccessible_object = message(_("sampleWidget-label-inaccessable-object"),
                                   "(inaccessible or missing object)")

# HTML fragments used more than once:
_query_row_template = "  <tr><th>%s</th>\n      <td>%s</td></tr>\n"

# Misc. helpers:
_nulljoin = "".join
_NLjoin = "\n".join


def getTerm(vocabulary, value):
    try:
        return vocabulary.getTerm(value)
    except LookupError:
        return BrokenTerm(value)


class BrokenTerm:
    """Term class used for terms that aren't currently available."""

    implements(ITokenizedTerm)

    getIcon = None
    title = _msg_inaccessible_object

    def __init__(self, value):
        self.token = value
        self.value = value


class SampleWidgetMixin(object):
    """Mix-in helper for behavior specific to sample values."""

    containerCssClass = "valueList"

    def convertTokensToValues(self, tokens, strict=False):
        # 'strict' must default to False since it needs that when
        # called from the base class
        # XXX assumes tokens and values are the same
        L = []
        for tok in tokens:
            try:
                v = self.vocabulary.getTermByToken(tok).value
            except LookupError:
                if strict:
                    raise WidgetInputError(
                        self.context.__name__,
                        self.context.title,
                        "token %r not found in vocabulary" % tok)
                v = tok
            L.append(v)
        return L

    def loadValueFromRequest(self):
        value = self.request.form.get(self.name) or None
        if self.queryview is not None:
            value = self.queryview.performAction(value)
        return value

    label_counter = 0

    def renderSelectionItem(self, type, name, term, selected, disabled):
        # Called from renderSelectionList().
        flag = ""
        if selected:
            flag = " checked='checked'"
        if disabled:
            flag += " disabled='disabled'"
        if flag:
            flag = "\n              " + flag
        count = self.label_counter
        self.label_counter += 1
        return ("<tr><td><input type='%s' value='%s'\n"
                "               name='%s'\n"
                "               id='%s-t%d'%s /></td>\n"
                "    <td><label for='%s-t%d'>\n"
                "        %s\n"
                "        %s</label></td></tr>"
                % (type, term.token, name, name, count, flag,
                   name, count, self.renderTermIcon(term),
                   self.renderTerm(term)))

    def renderTerm(self, term):
        # The returned value is not suitable for use as an HTML
        # attribute value.
        if term.getIcon is None:
            t = self.translate(term.title)
        else:
            t = term.title
        return escape(t)

    def renderTermIcon(self, term):
        if term.getIcon is None:
            return ("<strong class='sampleWidget-old-value'"
                    " title='(out-of-date value)'>X</strong>")
        else:
            return ("<img alt=%s src='%s' />"
                    % (quoteattr(term.title), term.getIcon))


class SampleMultiWidgetMixin(SampleWidgetMixin):

    def loadValueFromRequest(self):
        value = self.request.form.get(self.name, [])
        if not isinstance(value, list):
            value = [value]
        if self.queryview is not None:
            value = self.queryview.performAction(value)
        return value


# Display widgets:

class SampleDisplay(SampleWidgetMixin, widgetapi.BaseVocabularyDisplay):
    """Display widget for single-value sample value fields."""

    def render(self, value):
        if value in (widgetapi.NullValue, None):
            # missing single value
            return super(SampleDisplay, self).render(value)
        else:
            term = getTerm(self.vocabulary, value)
            pattern = "%s\n%s\n<input type='hidden' value=%s />"
            return pattern % (self.renderTermIcon(term),
                              self.renderTerm(term),
                              quoteattr(term.token))


class SampleBagDisplay(SampleMultiWidgetMixin,
                       widgetapi.BaseVocabularyBagDisplay):
    """Display widget for unordered multi-value sample value fields."""

    def render(self, value):
        return renderMultiDisplay(self, value)


class SampleListDisplay(SampleMultiWidgetMixin,
                        widgetapi.BaseVocabularyListDisplay):
    """Display widget for ordered multi-value sample value fields."""

    def render(self, value):
        return renderMultiDisplay(self, value)


def renderMultiDisplay(widget, value):
    if not value:
        # missing multiple value
        return widget.translate(widgetapi._msg_missing_multiple_value)
    else:
        pattern = ("<li>%s\n"
                   "    %s\n"
                   "    <input type='hidden' name=%s value=%s /></li>")
        vocabulary = widget.vocabulary
        L = []
        name = quoteattr(widget.name)
        for v in value:
            term = getTerm(vocabulary, v)
            L.append(pattern % (widget.renderTermIcon(term),
                                widget.renderTerm(term),
                                name,
                                quoteattr(term.token)))
        return ("<%s class=%s id=%s>\n%s\n</%s>"
                % (widget.containerElementType,
                   quoteattr(widget.containerCssClass),
                   quoteattr(widget.name),
                   "\n".join(L),
                   widget.containerElementType))



# Edit widgets:

def renderEditWidget(self, value):
    L = ["<div class=",
         quoteattr(self.containerCssClass),
         " id=",
         quoteattr(self.name),
         ">\n",
         self.renderValueArea(value),
         "\n"]
    if self.queryview is not None:
        L.append("<div class='widget-work-area'>\n")
        s = self.queryview.renderResults(value).rstrip()
        if s:
            s += "\n"
        L.extend([
            s,
            self.queryview.renderInput(),
            "\n</div>"
            ])
    L.append("</div>")
    return _nulljoin(L)

def renderSelectionList(widget, type, info, name):
    L = [widget.renderSelectionItem(type, name, *item) for item in info]
    return "<table>\n%s\n</table>" % _NLjoin(L)


class SampleEdit(ActionHelper, SampleWidgetMixin,
                 widgetapi.BaseVocabularyWidget):
    """Edit widget for single-value sample value fields."""

    def initialize(self):
        super(SampleEdit, self).initialize()
        self.addAction(CLEAR, _msg_clear)

    def loadValueFromRequest(self):
        value = super(SampleEdit, self).loadValueFromRequest()
        action = self.getAction()
        if action == CLEAR and not self.context.required:
            value = None
        return value

    def render(self, value):
        return renderEditWidget(self, value)

    def renderValueArea(self, value):
        disabled = False
        if value in (None, widgetapi.NullValue):
            disabled = True
            L = ["<span class='display'>",
                 self.translate(widgetapi._msg_missing_single_value),
                 "</span>"]
        else:
            term = getTerm(self.vocabulary, value)
            L = ["<span class='display'>",
                 self.renderTerm(term),
                 "</span>\n"
                 "<input type='hidden' name=",
                 quoteattr(self.name),
                 " value=",
                 quoteattr(term.token),
                 " />"]
        if not self.context.required:
            clear_disabled = value in (None, widgetapi.NullValue)
            L.extend(["\n<br />\n",
                      self.renderAction(CLEAR, clear_disabled)])
        return _nulljoin(L)


class SampleUniqueListEdit(ActionHelper, SampleMultiWidgetMixin,
                           widgetapi.BaseVocabularyWidget):
    """Edit widget for unique-list-valued sample value fields."""

    def initialize(self):
        super(SampleUniqueListEdit, self).initialize()
        self.addAction(MOVE_UP,   _msg_moveup)
        self.addAction(MOVE_DOWN, _msg_movedown)
        self.addAction(REMOVE,    _msg_remove)
        self.selections_name = self.name + ".picks"
        # Load supplemental data from request:
        L = self.request.form.get(self.selections_name, [])
        if not isinstance(L, list):
            L = [L]
        self.selections = self.convertTokensToValues(L)

    def loadValueFromRequest(self):
        value = super(SampleUniqueListEdit, self).loadValueFromRequest()
        action = self.getAction()
        if action == REMOVE:
            value = self.removeSelections(value)
        elif action == MOVE_UP:
            value = self.moveUp(value)
        elif action == MOVE_DOWN:
            value = self.moveDown(value)
        return value

    def removeSelections(self, value):
        for item in self.selections:
            if item in value:
                value.remove(item)
        return value

    def moveUp(self, value):
        """Move selected items toward the front of the list."""
        items = self.getMoveItems(value)
        # Things at the beginning of the list can't be moved up; skip
        # over leading selected items.
        start = 0
        while items and items[0][0] == start:
            del items[0]
            start += 1
        # Move the remaining items forward:
        self.moveByOffset(value, items, -1)
        return value

    def moveDown(self, value):
        """Move selected items toward the end of the list."""
        items = self.getMoveItems(value)
        # Ignore moves already at the end:
        end = len(value) - 1
        while items and items[-1][0] == end:
            del items[-1]
            end -= 1
        items.reverse()
        self.moveByOffset(value, items, +1)
        return value

    def getMoveItems(self, value):
        indexes = {}
        for item in self.selections:
            if item in value:
                indexes[value.index(item)] = item
        items = indexes.items()
        items.sort()
        return items

    def moveByOffset(self, value, items, offset):
        for i, item in items:
            del value[i]
            value.insert(i + offset, item)

    def render(self, value):
        return renderEditWidget(self, value)

    def renderValueArea(self, value):
        selections = [v for v in value if v in self.selections]
        items = [(getTerm(self.vocabulary, v), v in selections, False)
                 for v in value]
        if items:
            L = [renderSelectionList(self, "checkbox", items,
                                     self.selections_name),
                 self.renderAction(REMOVE),
                 self.renderAction(MOVE_UP, len(items) < 2),
                 self.renderAction(MOVE_DOWN, len(items) < 2),
                 ]
            current_value = _NLjoin(L)
        else:
            current_value = self.translate(
                widgetapi._msg_missing_multiple_value)
        L = ["<div class='value'>\n",
             current_value,
             "\n",
             _nulljoin([("<input name='%s' type='hidden' value=%s/>\n"
                         % (self.name, quoteattr(term.token)))
                        for (term, selected, disabled) in items]),
             "</div>"]
        return _nulljoin(L)


class SampleListEdit(SampleUniqueListEdit):
    """Edit widget for list-valued sample value fields."""

    def renderSelectionItem(self, type, name, term, selected, disabled):
        return super(SampleListEdit, self).renderSelectionItem(
            type, name, term, selected, False)


# Query views:

class BaseSampleQueryView(ActionHelper, widgetapi.BaseQueryView):

    queryResultBatchSize = 8

    def initialize(self):
        super(BaseSampleQueryView, self).initialize()
        self.addAction(QUERY, _msg_query)
        self.addAction(MORE, _msg_more)
        self.addAction(DISMISS, _msg_dismiss)
        name = self.name
        self.query_text_name = name
        self.query_index_name = name + ".start"
        self.selections_name = name + ".picks"
        # Load data from the form:
        get = self.request.form.get
        s = get(self.query_text_name, '')
        if isinstance(s, list):
            s = s[0]  # XXX ignore extra values
        self.query_text = s.strip()
        s = get(self.query_index_name) or None
        i = None
        if s:
            try:
                i = int(s)
            except ValueError:
                pass
            else:
                if i < 0:
                    i = None
        self.query_index = i
        selections = get(self.selections_name, [])
        if not isinstance(selections, list):
            selections = [selections]
        self.selections = self.widget.convertTokensToValues(selections,
                                                            strict=True)

    def performAction(self, value):
        self.action = self.getAction()
        if self.action == QUERY:
            self.query_index = 0
            self.selections = []
        elif self.action == MORE:
            self.selections = []
        elif self.action == DISMISS:
            self.query_index = None
            self.selections = []
        return value

    def renderInput(self):
        s = self.renderSupplementaryInput().rstrip()
        if s:
            s += "\n"
        L = ["<div class='query'>\n"
             "<table>\n",
             s]
        label = self.renderLabel(self.query_text_name,
                                 _msg_enter_search_text)
        widget = ("<input name='%s' id='%s' value=%s />"
                  % (self.query_text_name, self.query_text_name,
                     quoteattr(self.query_text)))
        L.extend((_query_row_template % (label, widget),
                  "</table>\n",
                  self.renderAction(QUERY),
                  "\n</div>"))
        return _nulljoin(L)

    def renderLabel(self, name, msgid):
        return ("<label for=%s>%s</label>"
                % (quoteattr(name), self.translate(msgid)))

    def renderQueryResults(self, results, value):
        info, more = self.computeResultInfo(results, value)
        L = ["<div class='results'>",
             "<input type='hidden' name='%s' value='%d' />"
             % (self.query_index_name, self.query_index),
             renderSelectionList(self.widget, self.selectionsType, info,
                                 self.selections_name),
             self.renderQueryResultsActions(more),
             self.renderAction(MORE, not more),
             self.renderAction(DISMISS),
             "</div>"]
        return _NLjoin(L)

    def renderSupplementaryInput(self):
        return ""

    def computeResultInfo(self, results, value):
        it = iter(results)
        if self.query_index:
            try:
                for i in range(self.query_index):
                    it.next()
            except StopIteration:
                return [], False
        more = True
        L = []
        for i in range(self.queryResultBatchSize):
            try:
                term = it.next()
            except StopIteration:
                more = False
                break
            else:
                L.append(self.resultInfoForTerm(term, value))
        else:
            try:
                it.next()
            except StopIteration:
                more = False
        return L, more


class SingleSelectionHelper(object):

    selectionsType = "radio"

    def initialize(self):
        super(SingleSelectionHelper, self).initialize()
        self.addAction(SELECT, _msg_select)

    def performAction(self, value):
        value = super(SingleSelectionHelper, self).performAction(value)
        if self.action == SELECT:
            if len(self.selections) == 1:
                value = self.selections[0]
                self.query_index = None
                self.selections = []
            else:
                # XXX some sort of advisory error...
                pass
        return value

    def renderQueryResultsActions(self, more):
        return self.renderAction(SELECT)

    def resultInfoForTerm(self, term, value):
        return term, term.value == value, False


class SampleQueryView(SingleSelectionHelper, BaseSampleQueryView):

    def getResults(self):
        if self.query_index is None:
            return None
        return self.context.query(self.query_text)


class FancySampleQueryView(SingleSelectionHelper, BaseSampleQueryView):

    def initialize(self):
        super(FancySampleQueryView, self).initialize()
        self.query_type_name = self.name + ".type"
        # Load data from the form:
        self.query_type = self.request.form.get(self.query_type_name) or None
        self.reference_types = self.context.getReferenceTypes()
        if self.query_type is not None:
            for term in self.reference_types:
                if term.token == self.query_type:
                    self.query_type = term.value
                    break
            else:
                self.query_type = None

    def getResults(self):
        if self.query_index is None:
            return None
        return self.context.query(self.query_text, type=self.query_type)

    def renderSupplementaryInput(self):
        content_types = self.reference_types
        len_content_types = len(content_types)
        if len_content_types > 1:
            L = []
            label = self.renderLabel(self.query_type_name,
                                     _msg_select_content_type)
            flags = ""
            if not self.query_type:
                flags = " selected"
            W = ["<select name='%s' id='%s'>\n"
                 % (self.query_type_name, self.query_type_name),
                 "          <option value=''%s>%s</option>\n"
                 % (flags, self.translate(_msg_any_content_type))]
            for ct in content_types:
                flags = ""
                if ct.value == self.query_type:
                    flags = " selected"
                W.append("          <option value='%s'%s>%s</option>\n"
                         % (ct.token, flags, ct.title))
            W.append("          </select>")
            widget = _nulljoin(W)
            L.append(_query_row_template % (label, widget))
            return _nulljoin(L)
        elif len_content_types == 1:
            # This use of iter() allows getReferenceTypes() to return
            # things other than sequences, like... vocabularies!
            return ("<input type='hidden' name='%s' value='%s' />"
                    % (self.query_type_name,
                       iter(content_types).next().token))
        else:
            return ""


class MultiSelectionHelper(object):

    selectionsType = "checkbox"

    def initialize(self):
        super(MultiSelectionHelper, self).initialize()
        self.addAction(ADD_DONE, _msg_add_done)
        self.addAction(ADD_MORE, _msg_add_more)

    def performAction(self, value):
        value = super(MultiSelectionHelper, self).performAction(value)
        if self.action == ADD_DONE:
            value = self.addSelections(value)
            self.query_index = None
        elif self.action == ADD_MORE:
            value = self.addSelections(value)
            self.query_index += self.queryResultBatchSize
            self.selections = []
        elif self.action == MORE:
            self.query_index += self.queryResultBatchSize
        return value

    def renderQueryResultsActions(self, more):
        return _NLjoin([self.renderAction(ADD_DONE),
                        self.renderAction(ADD_MORE, not more)])


class UniqueSelectionHelper(MultiSelectionHelper):

    def addSelections(self, value):
        for v in self.selections:
            if v not in value:
                value.append(v)
        return value

    def resultInfoForTerm(self, term, value):
        if value in (None, widgetapi.NullValue):
            disabled = False
            selected = term.value in self.selections
        else:
            disabled = term.value in value
            selected = disabled or term.value in self.selections
        return term, selected, disabled


class NonUniqueSelectionHelper(MultiSelectionHelper):

    def addSelections(self, value):
        value.extend(self.selections)
        return value

    def resultInfoForTerm(self, term, value):
        selected = term.value in self.selections
        if value not in (None, widgetapi.NullValue):
            selected = selected or term.value in value
        return term, selected, False


class SampleListQueryView(NonUniqueSelectionHelper, SampleQueryView):
    pass


class SampleUniqueListQueryView(UniqueSelectionHelper, SampleQueryView):
    pass


class FancySampleListQueryView(NonUniqueSelectionHelper,
                               FancySampleQueryView):
    pass


class FancySampleUniqueListQueryView(UniqueSelectionHelper,
                                     FancySampleQueryView):
    pass
