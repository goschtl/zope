import warnings

from zope import interface
from zope.publisher.browser import BrowserPage

from grokcore.component.interfaces import IContext

import grokcore.view
from grokcore.view import PageTemplate


class Model(object):
    interface.implements(IContext)


class View(BrowserPage, grokcore.view.ViewMixin):

    def __init__(self, context, request):
        super(View, self).__init__(context, request)
        self._initialize()

    def __call__(self):
        return self._update_and_render()

    def default_namespace(self):
        namespace = {}
        namespace['context'] = self.context
        namespace['request'] = self.request
        namespace['static'] = self.static
        namespace['view'] = self
        return namespace

    def __getitem__(self, key):
        # This is BBB code for Zope page templates only:
        if not isinstance(self.template, PageTemplate):
            raise AttributeError("View has no item %s" % key)

        value = self.template._template.macros[key]
        # When this deprecation is done with, this whole __getitem__ can
        # be removed.
        warnings.warn("Calling macros directly on the view is deprecated. "
                      "Please use context/@@viewname/macros/macroname\n"
                      "View %r, macro %s" % (self, key),
                      DeprecationWarning, 1)
        return value
