"""
A permission has to be defined first (using grok.Permission for example)
before it can be used in grok.require().

    >>> grok.testing.grok(__name__)
    Traceback (most recent call last):
    ...
    ConfigurationExecutionError: martian.error.GrokError: Undefined permission 'doesnt.exist' in <class 'grokcore.view.tests.security.missing_permission.MissingPermission'>. Use grok.Permission first.
    ...

"""
import zope.interface

from grokcore.view.tests import grok
import grokcore.view


class MissingPermission(grok.View):
    grok.context(zope.interface.Interface)
    grokcore.view.require('doesnt.exist')

    def render(self):
        pass
