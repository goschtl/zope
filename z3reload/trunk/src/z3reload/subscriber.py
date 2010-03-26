import sys

from zope.component import getGlobalSiteManager
from zope.publisher.interfaces import IRequest
from zope.component.registry import AdapterRegistration

from z3reload.reload import install_reloader, simple_view_classes
from z3reload.metaconfigure import enabled_classes, enabled_modules
from z3reload.metaconfigure import enabled_packages

request_type = IRequest


def is_simple_view(reg):
    """Return True if reg is a registration for a `simple` view.

    A `simple` view is one that subclasses one of simple_view_classes.
    """
    if not (isinstance(reg, AdapterRegistration) and
            len(reg.required) > 0 and
            reg.required[-1] is not None and
            reg.required[-1].isOrExtends(IRequest)):
        return False # this registration does not appear to be a view

    return (type(reg.factory) == type and
            issubclass(reg.factory, simple_view_classes))


def reload_enabled_for(view_class):
    """Return True if view_class should be made reloadable."""
    assert view_class.__bases__[-1] in simple_view_classes
    real_view = view_class.__bases__[0]
    if real_view in enabled_classes:
        return True
    for module in enabled_modules:
        if real_view.__module__ == module:
            return True
    for package in enabled_packages:
        if real_view.__module__.startswith(package):
            return True
    return False


def database_opened(event):
    """Scan adapter registrations and make specified views reloadable.

    Hooks on the DatabaseOpened event.
    """
    gsm = getGlobalSiteManager()
    for reg in gsm.registeredAdapters():
        if is_simple_view(reg) and reload_enabled_for(reg.factory):
            install_reloader(reg.factory)
