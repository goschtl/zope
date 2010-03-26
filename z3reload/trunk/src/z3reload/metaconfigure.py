import sys
from zope.configuration.exceptions import ConfigurationError


enabled_classes = [] # list of class objects
enabled_modules = [] # list of module names
enabled_packages = [] # list of package names


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
