====================================
Overriding Python's Standard Library
====================================


Rationale
---------

The pythonlib directory is used for the specific purpose of
overriding modules in the Python standard library.  However, you
may only override by installing versions of a module or package
from a newer version of Python.  You may *not* make changes to a
module that deviates from some version in Python.

For example, say that Zope's current minimal Python requirement is
Python 2.2.3, but say that you need the ``gettext`` module from
Python 2.3.  You may take the ``gettext`` module from Python 2.3
and drop it in the pythonlib/compat22 directory and arrange your
imports so that Zope uses this version of ``gettext`` instead of
the Python 2.2.3 standard module (see below for details).

The problem with making changes that aren't reflected in Python
releases is that you will not be able to remove pythonlib modules
when Zope's minimal requirement changes, because of the version
skew.  The whole point of the pythonlib directory is so that when
Zope's minimal Python version becomes Python 2.3, we can get rid
of pythonlib/compat22 and everything will still just work.  We
can't do that if there are changes to modules in pythonlib that
don't exist in Python versions.

It is okay to copy modules here from Python CVS.


Use in Zope code
----------------

Here's an example from Zope code for using the overridden
``gettext`` module.  Instead of::

    import gettext

do::

    from pythonlib import gettext

If you're using Python 2.2.x you'll get the overridden ``gettext``
module.  If you're using Python 2.3, you'll get the standard library
module.


Adding new overrides
--------------------

For each override, there is a wrapper module in pythonlib and the real
overridden module in pythonlib/compatXY where X and Y are the
major/minor version numbers for the Python version you need to
override.  Thus ``pythonlib.gettext`` is a shim for
``pythonlib.compat22.gettext`` for Python 2.2, but it is a shim for
the standard ``gettext`` module in Python 2.3.  Zope code doesn't care
as it will always use the shim anyway.

To add a new override, first decide what versions of Python you
want to override, then make sure that the pythonlib/compatXY
directory for that version exists.  If not, create it as a
package.

Note: we currently don't care about micro releases.  I think
that's a yagni (some might say a yagni inside a yagni :).

Next, put the new version of the module -- i.e. the override -- in
pythonlib/compatXY.  Do *not* put it in any compat directory you do
not want to override!  If the machinery below doesn't find an
override, specifically it gets an ``ImportError``, then it will just
use the standard library module.

Next, in your shim module, put the following two lines (after any
ZPL and module docstrings of course)::

    from pythonlib import load_compat
    load_compat('gettext', globals())

where ``gettext`` would be replaced with whatever module you're
actually importing.

The ``load_compat()`` function does all the work and implements
the import policy.
