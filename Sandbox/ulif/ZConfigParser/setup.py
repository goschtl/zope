README = open("README.txt").read()
NEWS = open("NEWS.txt").read()

def alltests():
    import os
    import sys
    from unittest import TestSuite
    # use the zope.testing testrunner machinery to find all the
    # test suites we've put under ourselves
    from zope.testing.testrunner import get_options
    from zope.testing.testrunner import find_suites
    from zope.testing.testrunner import configure_logging
    configure_logging()
    here = os.path.abspath(os.path.dirname(sys.argv[0]))
    args = sys.argv[:]
    defaults = ["--test-path", here]
    options = get_options(args, defaults)
    suites = list(find_suites(options))
    return TestSuite(suites)

options = dict(
    name="ZConfigParser",
    version="0.1dev",
    author="Uli Fouquet based on work of members of the Zope community.",
    author_email="zope-dev@zope.org",
    description="Structured Configuration Library based on ConfigParser",
    long_description=README + "\n\n" + NEWS,
    license="ZPL 2.1",
    url="http://pypi.python.org/pypi/zconfigparser",
    # List packages explicitly so we don't have to assume setuptools:
    packages=[
        "ZConfigParser",
        "ZConfigParser.components",
        "ZConfigParser.components.basic",
        "ZConfigParser.components.basic.tests",
        "ZConfigParser.components.logger",
        "ZConfigParser.components.logger.tests",
        "ZConfigParser.tests",
        "ZConfigParser.tests.library",
        "ZConfigParser.tests.library.thing",
        "ZConfigParser.tests.library.widget",
        ],
    scripts=["scripts/zconfig", "scripts/zconfig_schema2html"],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    # Support for 'setup.py test' when setuptools is available:
    test_suite="__main__.alltests",
    tests_require=[
        "zope.testing",
        ],
    )

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(**options)
