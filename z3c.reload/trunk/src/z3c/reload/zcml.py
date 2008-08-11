import sys
from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import Tokens, GlobalObject
from zope.interface import Interface

enabled_classes = [] # list of class objects
enabled_modules = [] # list of module names
enabled_packages = [] # list of package names

class IReloadDirective(Interface):

    classes = Tokens(
        title=u"View classes",
        required=False,
        value_type=GlobalObject(
                title=u"View class",
                description=u"""
                A view class for which automatic reload should be enabled.
                """))

    modules = Tokens(
        title=u"Modules",
        required=False,
        value_type=GlobalObject(
                title=u"Module",
                description=u"""
                A module containing views for which automatic reload should be
                enabled.
                """))

    packages = Tokens(
        title=u"Packages",
        required=False,
        value_type=GlobalObject(
            title=u"Package",
            description=u"""
            A package containing views for which automatic reload should be
            enabled.

            `module` only works for a single module, whereas `package` also
            applies for contained modules and packages.
            """))


def handle_reload(classes, modules, packages):
    """Add provided objects to global registry of reloadable objects."""
    enabled_classes.extend(classes)
    enabled_modules.extend([mod.__name__ for mod in modules])
    enabled_packages.extend([pkg.__name__ for pkg in packages])


def reload(_context, classes=[], modules=[], packages=[]):
    """Process the `reload` ZCML directive."""
    if not (classes or modules or packages):
        raise ConfigurationError("You must specify at least one of"
                                 " `classes`, `modules` or `packages`.")
    _context.action(discriminator=None, callable=handle_reload,
                    args=(classes, modules, packages))
