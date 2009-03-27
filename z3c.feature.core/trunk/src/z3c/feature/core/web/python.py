from z3c.form.form import EditForm
from z3c.form.field import Fields

from z3c.feature.core.python import PythonInterpreterFeature
from z3c.feature.core.python import ScriptFeature
from z3c.feature.core import interfaces


class PythonInterpreterWebView(EditForm):
    fields = Fields(interfaces.IPythonInterpreterFeature).select('executableName')

class PythonInterpreterWebFeature(object):
    viewFactory = PythonInterpreterWebView
    contentFactory = PythonInterpreterFeature
    title = u'Python Interpreter'
    description = (u"Adds a Python interpreter with all the path "
                   u"information needed to make project code available.")


class ScriptWebView(EditForm):

    fields = Fields(interfaces.IScriptFeature)

    def update(self):
        super(ScriptWebView, self).update()
        self.label = self.context.featureTitle

class ScriptWebFeature(object):
    viewFactory = ScriptWebView
    contentFactory = ScriptFeature
    title = u'Console Script'
    description = (u"Adds an entry point for setuptools to create a "
                   u"console script that runs a python function. "
                   u"Great for projects that run from the command line "
                   u"and require insanely easy installation.")
