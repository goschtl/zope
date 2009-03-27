##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Core Python Features

$Id$
"""
import zope.interface
from zope.schema.fieldproperty import FieldProperty

from z3c.builder.core import project, buildout
from z3c.builder.core.python import ModuleBuilder, FunctionBuilder
from z3c.feature.core import base, interfaces, xml


PYTHON_INTERPRETER_DOCUMENTATION = """
The Python Interpreter feature creates an alias to whatever python
interpreter you want inside your project's bin/ directory.
Furthermore, it adds your project and all its egg dependencies to the
python path.  After running buildout from your project directory you
can start up the interpreter as normal::

  $ ./bin/python

  >>> from myproject import mymodule
  >>> form a.dependency import something
"""

SCRIPT_FEATURE_DOCUMENTATION = """
The Command Line Script Feature exposes a python function in your
project as a command line script.  There are several pieces to this:

  #. **The script file.**

        There is a script file located at %(scriptFile)s with a function
        in it called %(scriptFunction)s.  This is what you should modify to
        make your script actually do something.

  #. **Setuptools entry point.**

       When someone installs your project using setuptools, for example
       with the command::

         $ easy_install yourproject

       any entry points in the console_script group will turn into
       executable scripts that the end user can just run.  This make your
       project into an application and not just a set of python
       libraries.

       The entry point is created by modifying the ``setup.py`` file.
       Look for the keyword parameter called entry_points.

  #. ``scripts`` **buildout part.**

       Finally there is also a part added to buildout.cfg that makes the
       script defined in the entry point available in the projects bin/
       directory.  This is only for development purposes.
"""

class PythonInterpreterFeature(base.BaseFeature):
    zope.interface.implements(interfaces.IPythonInterpreterFeature)

    executableName = FieldProperty(
        interfaces.IPythonInterpreterFeature['executableName'])

    featureTitle = u'Python Interpreter'
    featureDocumentation = PYTHON_INTERPRETER_DOCUMENTATION

    def _applyTo(self, context):
        pythonPartBuilder = buildout.PartBuilder(u'python')
        pythonPartBuilder.addValue('recipe', 'zc.recipe.egg')
        pythonPartBuilder.addValue('interpreter', self.executableName)
        pythonPartBuilder.addValue('eggs', context.name)
        context.buildout.add(pythonPartBuilder)


class ScriptFeature(base.BaseFeature):
    zope.interface.implements(interfaces.IScriptFeature)

    scriptName = FieldProperty(interfaces.IScriptFeature['scriptName'])
    scriptFile = FieldProperty(interfaces.IScriptFeature['scriptFile'])
    scriptFunction = FieldProperty(interfaces.IScriptFeature['scriptFunction'])

    featureTitle = u'Command Line Script'

    @property
    def featureDocumentation(self):
        return SCRIPT_FEATURE_DOCUMENTATION % dict(
            scriptFunction=self.scriptFunction,
            scriptFile=self.scriptFile)

    def _applyTo(self, context):
        scriptName = self.scriptName or context.name
        moduleBuilder = ModuleBuilder(self.scriptFile)
        moduleBuilder.add(FunctionBuilder(
            self.scriptFunction,
            kwargs={'args':None},
            docstring=('Runs the %s script '
                       'from the %s project') % (scriptName, context.name),
            code='print "Successfully ran the %s script"' % scriptName
            ))

        context.package.add(moduleBuilder)

        context.setup.addEntryPoints(
            'console_scripts', ['%s = %s.%s:%s' % (scriptName,
                                                   context.name,
                                                   self.scriptFile[:-3],
                                                   self.scriptFunction)])

        scriptsPart = buildout.PartBuilder(u'scripts')
        scriptsPart.addValue('recipe','zc.recipe.egg:scripts')
        scriptsPart.addValue('eggs', context.name)
        scriptsPart.addValue('script', scriptName)
        context.buildout.add(scriptsPart)
