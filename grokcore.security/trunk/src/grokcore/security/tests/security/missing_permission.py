"""
A permission has to be defined first (using grok.Permission for example)
before it can be used in grok.require().

    >>> grok.testing.grok(__name__)
    Traceback (most recent call last):
    ...
    ConfigurationExecutionError: martian.error.GrokError: Undefined permission 'doesnt.exist' in <class 'grok.tests.security.missing_permission.MissingPermission'>. Use grok.Permission first.
    ...

"""

import grokcore.security as grok

class MissingPermission(object):
    grok.require('doesnt.exist')

    def render(self):
        pass

