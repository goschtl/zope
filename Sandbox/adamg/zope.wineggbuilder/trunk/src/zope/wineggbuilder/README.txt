
Install mocks:

    >>> from zope.wineggbuilder import base
    >>> from zope.wineggbuilder import build
    >>> from zope.wineggbuilder import testing

    >>> oldSVNcommand = base.SVN.commandKlass
    >>> base.SVN.commandKlass = testing.MockCommand()

    >>> oldCompilerCommand = build.Compiler.commandKlass
    >>> build.Compiler.commandKlass = testing.MockCommand()

    >>> oldPYPI = build.Package.pypiKlass
    >>> build.Package.pypiKlass = testing.MockPYPI()

    >>> oldURLgetter = build.Package.urlGetterKlass
    >>> build.Package.urlGetterKlass = testing.MockURLGetter()


    >>> import os.path
    >>> testininame = os.path.join(os.path.dirname(build.__file__), 'test.ini')
    >>> build.main([testininame, '-v'])


    >>> from pprint import pprint
    >>> pprint(testing.MOCKLOG)


Remove mocks:

    >>> base.SVN.commandKlass = oldSVNcommand
    >>> build.Compiler.commandKlass = oldCompilerCommand
    >>> build.Package.pypiKlass = oldPYPI
    >>> build.Package.urlGetterKlass = oldURLgetter
