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
"""Alternate base classes for IBrowserWidget implementations.

The base classes provided here implement the IBrowserWidget API and
provide a simpler API that derived classes are expected to implement.

$Id$
"""
from xml.sax.saxutils import escape, quoteattr

from zope.interface import implements
from zope.i18n.messageid import MessageIDFactory

from zope.app.form.browser.interfaces import IBrowserWidget
from zope.app.form.interfaces import WidgetInputError


DOMAIN = "zope-widget-examples"

_ = MessageIDFactory(DOMAIN)


def message(msgid, default):
    # XXX This treats MessageID objects as mutable objects, but is
    # only used when the MessageID is first created.  Using a separate
    # function is needed since the message catalog tools require that
    # _() take exactly one positional string literal argument, else we
    # could just call the MessageID constructor directly.
    assert msgid.default == msgid
    assert msgid.domain == DOMAIN
    msgid.default = default
    return msgid


# Since NullValue must be a singleton, be safe in the face of
# reload():
try:
    NullValue
except NameError:
    NullValue = object()


_msg_missing_single_value = message(
    _("widget-missing-single-value"),   "(no value)")
_msg_missing_multiple_value = message(
    _("widget-missing-multiple-value"), "(no values)")


class BaseWidget(object):
    implements(IBrowserWidget)

    name = property(lambda self: self.__prefix + self.context.__name__)
    required = property(lambda self: self.context.required)
    title = property(lambda self: self.context.title)

    __initialized = False
    __initial_value = NullValue
    __prefix = "field."

    def __init__(self, context, request):
        self.context = context
        self.request = request

    # Form management methods.
    # Subclasses should not to override these.

    def getInputValue(self):
        if not self.__initialized:
            self.__initialize()
        return self.__computed_value

    def hasInput(self):
        marker_name = self.name + "-marker"
        return marker_name in self.request.form

    def setRenderedValue(self, value):
        assert (self.__initial_value is NullValue
                or (not self.__initialized)
                or self.__initial_value == value)
        self.__initial_value = value

    def setPrefix(self, prefix):
        assert not self.__initialized
        if prefix[-1] != ".":
            prefix += "."
        self.__prefix = prefix

    def __initialize(self):
        self.__initialized = True
        self.initialize()
        if self.hasInput():
            self.__computed_value = self.loadValueFromRequest()
        elif self.__initial_value is NullValue:
            self.__computed_value = self.context.default
        else:
            self.__computed_value = self.__initial_value

    def applyChanges(self, content):
        field = self.context
        value = self.getInputValue()
        change = field.query(content, self) != value
        if change:
            field.set(content, value)
        return change

    # Rendering methods:
    # (These should not need to be overridden.)

    def __call__(self):
        if not self.__initialized:
            self.__initialize()
        marker_name = self.name + "-marker"
        marker = "<input type='hidden' name='%s' value='x' />\n" % marker_name
        return marker + self.render(self.__computed_value)

    def row(self):
        return ("<div class='label'>%s</div>\n"
                "<div class='field'>%s</div>"
                % (self.label(), self()))

    def translate(self, msgid):
        return msgid.default

    # API for subclasses to implement:

    def initialize(self):
        """Initialize internal data structures needed by the widget.

        This method should not load values from the request.

        Derived classes should call the base class initialize() before
        performing specialized initialization.  This requirement is
        waived for classes which inherit directly from, and *only*
        from, BaseWidget.
        """

    def label(self):
        # Subclasses may want to override this.
        return escape(self.title)

    def loadValueFromRequest(self):
        """Load the value from data in the request."""
        raise NotImplementedError(
            "BaseWidget subclasses must implement loadValueFromRequest()")

    def render(self, value):
        raise NotImplementedError(
            "BaseWidget subclasses must implement render()")


class BaseVocabularyWidget(BaseWidget):

    query = None
    queryview = None

    def __init__(self, context, request):
        super(BaseVocabularyWidget, self).__init__(context, request)
        self.vocabulary = context

    # Helpers used by the vocabulary widget machinery;
    # these should not be overriden.

    def setField(self, field):
        assert self.context is self.vocabulary
        # only allow this to happen for a bound field
        assert field.context is not None
        self.context = field

    def setQuery(self, query, queryview):
        assert self.query is None
        assert self.queryview is None
        assert query is not None
        assert queryview is not None
        self.query = query
        self.queryview = queryview

        # Use of a hyphen to form the name for the query widget
        # ensures that it won't clash with anything else, since
        # field names are normally Python identifiers.
        queryview.setName(self.name + "-query")

    # Override the methods in the subclass interface:

    def initialize(self):
        """Make sure the query view has a chance to initialize itself."""
        if self.queryview is not None:
            self.queryview.initialize()

    def loadValueFromRequest(self):
        """Load the value from data in the request.

        If self.queryview is not None, this method is responsible for
        calling the query view's performAction() method with the value
        loaded, and returning the result::

            value = ...load value from request data...
            if self.queryview is not None:
                value = self.queryview.performAction(value)
            return value
        """
        return super(BaseVocabularyWidget, self).loadValueFromRequest()

    # Convenience method:

    def convertTokensToValues(self, tokens):
        """Convert a list of tokens to a list of values.

        If an invalid token is encountered, WidgetInputError is raised.
        """
        L = []
        for token in tokens:
            try:
                term = self.vocabulary.getTermByToken(token)
            except LookupError:
                raise WidgetInputError(
                    self.context.__name__,
                    self.context.title,
                    "token %r not found in vocabulary" % token)
            else:
                L.append(term.value)
        return L


class BaseVocabularyDisplay(BaseVocabularyWidget):

    def render(self, value):
        if value in (NullValue, None):
            # missing single value
            return self.translate(_msg_missing_single_value)
        else:
            return self.renderTerm(self.vocabulary.getTerm(value))

    def renderTerm(self, term):
        """Return textual presentation for term."""
        raise NotImplementedError("BaseVocabularyMultiDisplay subclasses"
                                  " must implement renderTerm()")


class BaseVocabularyMultiDisplay(BaseVocabularyDisplay):
    """Base class for display widgets of multi-valued vocabulary fields."""

    def render(self, value):
        if not value:
            # missing multiple value
            return self.translate(_msg_missing_multiple_value)
        else:
            pattern = ("<li>%s\n"
                       "    <input type='hidden' name=%s value=%s /></li>")
            vocabulary = self.vocabulary
            L = []
            name = quoteattr(self.name)
            for v in value:
                term = vocabulary.getTerm(v)
                L.append(pattern % (self.renderTerm(term), name,
                                    quoteattr(term.token)))
            return ("<%s class=%s id=%s>\n%s\n</%s>"
                    % (self.containerElementType,
                       quoteattr(self.containerCssClass),
                       quoteattr(self.name),
                       "\n".join(L),
                       self.containerElementType))

    containerCssClass = "values"


class BaseVocabularyBagDisplay(BaseVocabularyMultiDisplay):
    """Base class for display widgets of unordered multi-valued
    vocabulary fields."""

    containerElementType = "ul"


class BaseVocabularyListDisplay(BaseVocabularyMultiDisplay):
    """Base class for display widgets of ordered multi-valued
    vocabulary fields."""

    containerElementType = "ol"


class BaseQueryView(object):

    name = None
    widget = None
    __initialized = False

    def __init__(self, context, request):
        self.context = context
        self.request = request

    # Methods called by the vocabulary widget construction machinery;
    # subclasses should not need to override these.

    def setName(self, name):
        assert not self.__initialized
        assert not name.endswith(".")
        assert self.name is None
        self.name = name

    def setWidget(self, widget):
        assert not self.__initialized
        assert self.widget is None
        assert widget is not None
        self.widget = widget

    # Methods which may be overriden by subclasses:

    def initialize(self):
        """Initialization which does not require reading the request.

        Derived classes should call the base class initialize() before
        performing specialized initialization.
        """
        # Should loading from the request happen here?
        assert self.name is not None
        assert self.widget is not None
        assert not self.__initialized
        self.__initialized = True

    def renderResults(self, value):
        """Render query results if we have any, otherwise return an
        empty string.
        """
        results = self.getResults()
        if results is None:
            return ""
        else:
            return self.renderQueryResults(results, value)

    # Methods which should be overriden by subclasses:

    def performAction(self, value):
        """Perform any modifications to the value based on user actions.

        This method should be overriden if the query view provides any
        actions which can modify the value of the field.
        """
        return value

    # Methods which must be overriden by subclasses:

    def getResults(self):
        """Perform the query, or return None.

        The return value should be None if there is no query to
        execute, or an object that can be rendered as a set of results
        by renderQueryResults().

        If the query results in an empty set of results, some value
        other than None should be used to represent the results so
        that renderQueryResults() can provide a helpful message.
        """
        raise NotImplementedError(
            "BaseQueryView subclasses must implement getResults()")

    def renderInput(self):
        """Render the input area of the query view."""
        raise NotImplementedError(
            "BaseQueryView subclasses must implement renderInput()")

    def renderQueryResults(self, results, value):
        """Render the results returned by getResults()."""
        raise NotImplementedError(
            "BaseQueryView subclasses must implement renderQueryResults()")
