"""testrunner - a Zope test suite utility.

The testrunner utility is used to execute PyUnit test suites. You can find
more information on PyUnit at http://pyunit.sourceforge.net. This utility
should be run from the root of your Zope installation. It will set up the
correct python path environment based on your installation directory so that
test suites can import Zope modules in a way that is fairly independent of
the location of the test suite. It does *not* import the Zope package, so
a test thats depend on dynamic aspects of the Zope environment (such as
SOFTWARE_HOME being defined) may need to 'import Zope' as a part of the
test suite.

Testrunner will look for and execute test suites that follow some simple
conventions. Test modules should have a name prefixed with 'test', such as
'testMyModule.py', and test modules are expected to define a module function
named 'test_suite' that returns a PyUnit TestSuite object. By convention,
we put test suites in 'tests' subdirectories of the packages they test.

Testrunner is used to run all checked in test suites before releases are
made, and can be used to quickly run a particular suite or all suites in
a particular directory."""

import sys, os, imp, string, getopt

pyunit=None


class TestRunner:
    """Test suite runner"""

    def __init__(self, basepath):
        # initialize python path
        self.basepath=path=basepath
        pjoin=os.path.join
        if sys.platform == 'win32':
            sys.path.insert(0, pjoin(path, 'lib/python'))
            sys.path.insert(1, pjoin(path, 'bin/lib'))
            sys.path.insert(2, pjoin(path, 'bin/lib/plat-win'))
            sys.path.insert(3, pjoin(path, 'bin/lib/win32'))
            sys.path.insert(4, pjoin(path, 'bin/lib/win32/lib'))
            sys.path.insert(5, path)
        else:
            sys.path.insert(0, pjoin(path, 'lib/python'))
            sys.path.insert(1, path)

        global pyunit
        import unittest
        pyunit=unittest

    # modules that would match, but are not (yet) PyUnit tests.
    skip_names={'testrunner.py': None,
                'test_logger.py': None,
                'test_MultiMapping.py': None,
                'test_Sync.py': None,
                'test_ThreadLock.py': None,
                'test_acquisition.py': None,
                'test_add.py': None,
                'test_binding.py': None,
                'test_explicit_acquisition.py': None,
                'test_func_attr.py': None,
                'test_method_hook.py': None,
                'test.py': None,
                }

    skip_name=skip_names.has_key

    def getSuiteFromFile(self, filepath):
        if not os.path.isfile(filepath):
            raise ValueError, '%s is not a file' % filepath
        path, filename=os.path.split(filepath)
        name, ext=os.path.splitext(filename)
        file, pathname, desc=imp.find_module(name, [path])
        try:     module=imp.load_module(name, file, pathname, desc)
        finally: file.close()
        function=getattr(module, 'test_suite', None)
        if function is None:
            return None
        return function()

    def runSuite(self, suite):
        runner=pyunit.TextTestRunner()
        runner.run(suite)

    def report(self, message):
        print message
        print

    def runAllTests(self):
        """Run all tests found in the current working directory and
           all subdirectories."""
        self.runPath(self.basepath)

    def runPath(self, pathname):
        """Run all tests found in the directory named by pathname
           and all subdirectories."""
        names=os.listdir(pathname)
        skip_name = self.skip_name
        for name in names:
            fname, ext=os.path.splitext(name)
            if name[:4]=='test' and name[-3:]=='.py' and \
               (not skip_name(name)):
                filepath=os.path.join(pathname, name)
                self.runFile(filepath)
        for name in names:
            fullpath=os.path.join(pathname, name)
            if os.path.isdir(fullpath):
                self.runPath(fullpath)

    def runFile(self, filename):
        """Run the test suite defined by filename."""
        self.report('Running: %s' % filename)
        try:    suite=self.getSuiteFromFile(filename)
        except: suite=None
        if suite is None:
            self.report('No test suite found in file:\n%s' % filename)
            return
        self.runSuite(suite)







def main(args):

    usage_msg="""Usage: python testrunner.py [options]

    If run without options, testrunner will run all test suites
    found in all subdirectories of the current working directory. 

    options:

       -a

          Run all tests found in all subdirectories of the current
          working directory. This is the default if no options are
          specified.

       -d dirpath

          Run all tests found in the directory specified by dirpath,
          and recursively in all its subdirectories. The dirpath
          should be a full system path.

       -f filepath

          Run the test suite found in the file specified. The filepath
          should be a fully qualified path to the file to be run.\n"""

    pathname=None
    filename=None
    test_all=None

    try:
        options, arg=getopt.getopt(args, 'ad:f:')
        for name, value in options:
            name=name[1:]
            if name == 'a':
                test_all=1
            elif name == 'd':
                pathname=string.strip(value)
            elif name == 'f':
                filename=string.strip(value)
            else:
                err_exit(usage_msg)
        if not options:
            test_all=1
    except:
        err_exit(usage_msg)

    testrunner=TestRunner(os.getcwd())
    if test_all:
        testrunner.runAllTests()
    elif pathname:
        testrunner.runPath(pathname)
    elif filename:
        testrunner.runFile(filename)
    sys.exit(0)


def err_exit(message):
    sys.stderr.write("\n%s\n" % message)
    sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
