from os import curdir
from os.path import join, abspath, dirname, split

def process():
    """Read in zope.conf configuration file.

    This is a hack but there doesn't seem to be a better way.
    """
    try:
        __file__
    except NameError:
        # Test was called directly, so no __file__ global exists.
        _prefix = abspath(curdir)
    else:
        # Test was called by another test.
        _prefix = abspath(dirname(__file__))

    from Zope.Startup.run import configure
    configure(join(_prefix, '..', '..', '..', 'etc', 'zope.conf'))
