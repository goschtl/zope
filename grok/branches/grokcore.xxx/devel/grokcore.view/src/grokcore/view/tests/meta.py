from zope import component
from zope.security.checker import NamesChecker, defineChecker
from zope.security.interfaces import IPermission

import martian
from martian.error import GrokError

from grokcore.view.meta import ViewGrokkerBase
import grokcore.view


def make_checker(factory, view_factory, permission, method_names=None):
    """Make a checker for a view_factory associated with factory.

    These could be one and the same for normal views, or different
    in case we make method-based views such as for JSON and XMLRPC.
    """

    if method_names is None:
        method_names = ['__call__']
    if permission is not None:
        check_permission(factory, permission)
    if permission is None or permission == 'zope.Public':
        checker = NamesChecker(method_names)
    else:
        checker = NamesChecker(method_names, permission)
    defineChecker(view_factory, checker)


def check_permission(factory, permission):
    """Check whether a permission is defined.

    If not, raise error for factory.
    """
    if component.queryUtility(IPermission,
                              name=permission) is None:
        raise GrokError('Undefined permission %r in %r. Use '
                        'grok.Permission first.'
                        % (permission, factory), factory)


class ViewGrokker(ViewGrokkerBase):
    martian.component(grokcore.view.ViewMixin)

    def protectName(self, config, factory, permission):
        config.action(
            discriminator=('protectName', factory, '__call__'),
            callable=make_checker,
            args=(factory, factory, permission),
            )
