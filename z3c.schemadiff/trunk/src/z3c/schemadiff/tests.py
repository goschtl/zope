from zope import component
from zope import interface
from zope import schema
import doctest
import zope.component.testing


OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def test_suite():
    globs = dict(interface=interface, component=component, schema=schema)

    return doctest.DocFileSuite(
        'README.txt',
        optionflags=OPTIONFLAGS,
        setUp=zope.component.testing.setUp,
        tearDown=zope.component.testing.tearDown,
        globs=globs,
        package="z3c.schemadiff")
