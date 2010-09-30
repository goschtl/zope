import sys
from zope.app.pagetemplate.simpleviewclass import simple as SimplePTPage
from zope.app.publisher.browser.viewmeta import simple as SimplePage
from zope.publisher.browser import BrowserPage
from zope.viewlet import viewlet, manager
from z3c.pagelet.browser import BrowserPagelet

from z3c.reload import BLATHER

simple_view_classes = (
    SimplePTPage, SimplePage, BrowserPage,
    viewlet.ViewletBase, manager.ViewletManagerBase,
    BrowserPagelet)


class Reloader(object):
    """A mixin to be used on SimpleViewClass instances.

    These SimpleViewClass instances are in fact dynamically constructed types
    with either zope.app.pagetemplate.simpleviewclass.simple or
    zope.app.publisher,browser.viewmeta as one of the base classes.

    This mixin must be the first superclass, because its __init__ must be
    called on instantiation.
    """

    def __init__(self, *args, **kw):
        bases = self.__class__.__bases__
        assert len(bases) >= 2
        reloader2, real_view = bases[:2]
        assert reloader2 is Reloader

        rest = bases[2:]

        clsname = real_view.__name__
        modname = real_view.__module__
        module = sys.modules[modname]
        if hasattr(module, clsname):
            reload(module)
            new_view = getattr(module, clsname)
            self.__class__.__bases__ = (Reloader, new_view) + rest
        else:
            # If the module does not have such an attribute, chances are that
            # the class was dynamically constructed.  In this case reloading is
            # likely to break so we don't do it.
            new_view = real_view # just use the old view

        self.__sanitize_bases(new_view)
        # This is generally not the right thing to do, but should work in this
        # limited case.
        for base in self.__class__.__bases__[1:]:
            try:
                base.__init__(self, *args, **kw)
            except TypeError:
                # Needed as object.__init__() does not accept any arguments in py26.
                base.__init__(self)

    def __sanitize_bases(self, cls):
        """Make sure that the bases of a class are in the scope.

        This works around the problem when a class bases do not correspond
        to the same-named classes in the scope, which could happen after a
        reload.  This causes errors when invoking base clases
        """
        modname = cls.__module__
        module = sys.modules[modname]

        bases = cls.__bases__
        new_bases = []
        for b in bases:
            bc = getattr(module, b.__name__, None)
            if bc is not None and bc.__module__ != modname:
                # Make sure that the base class comes from a different module.
                new_base = getattr(module, b.__name__)
                self.__sanitize_bases(new_base)
                new_bases.append(new_base)
            else:
                # Couldn't find class in local scope, abort.
                break
        else:
            # All bases checked successfully.
            cls.__bases__ = tuple(new_bases)



def install_reloader(view_class):
    """Install the Reloader mixin on view_class."""
    if BLATHER:
        print >> sys.stderr, 'Reloader installed for', view_class.__bases__[0]
    view_class.__bases__ = (Reloader, ) + view_class.__bases__
