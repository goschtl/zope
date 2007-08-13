"""Silly example code to show usage of grok.testing:
"""

import grok

class SampleApp(grok.Application, grok.Container):
    pass

class MyTest0(grok.testing.FunctionalDocTest):
    """A test without file."""

class MyTest1(grok.testing.FunctionalDocTest):
    """A test with one file."""
    grok.testing.file('README.txt')

class MyTest2(grok.testing.FunctionalDocTest):
    """A test with two files."""
    grok.testing.file('README.txt')
    grok.testing.file('Another.txt')

class MyTest3(grok.testing.FunctionalDocTest):
    # This is currently not supported...
    grok.context(SampleApp)
