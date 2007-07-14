import sys
import os.path
import shutil
from paste.script.templates import var, NoDefault, Template, BasicPackage

class Deploy(Template):
    _template_dir = 'deploy'
    summary = "Deployment of a Zope application"

    vars = [
        var('user', 'Name of an initial administrator user', default=NoDefault),
        var('passwd', 'Password for the initial administrator user',
            default=NoDefault),
        var('eggs_dir', 'Location where zc.buildout will look for and place '
            'packages', default=os.path.expanduser('~/buildout-eggs'))
        ]

    def check_vars(self, vars, cmd):
        vars = super(Deploy, self).check_vars(vars, cmd)
        vars['eggs_dir'] = os.path.expanduser(vars['eggs_dir'])
        return vars

class ZopeApp(Template):
    _template_dir = 'zope_app'
    summary = 'Package that contains a Zope application'
    required_templates = ['deploy']

class GrokApp(Deploy):

    vars = [
        var('module', 'Name of a demo Python module placed into the package',
            default='app.py')
        ] + Deploy.vars

    def check_vars(self, vars, cmd):
        vars = super(GrokApp, self).check_vars(vars, cmd)
        module = vars['module']
        if '.' in module:
            if module.endswith('.py'):
                vars['module'] = module[:-3]
            else:
                raise command.BadCommand('Bad module name: %s' % module)
        if vars['package'] in ('grok', 'zope'):
            print
            print "Error: The chosen project name results in an invalid " \
                  "package name: %s." % vars['package']
            print "Please choose a different project name."
            sys.exit(1)
        return vars
