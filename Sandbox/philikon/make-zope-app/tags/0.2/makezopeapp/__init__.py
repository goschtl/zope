import sys
import os.path
from paste.script import templates, command
from paste.script.templates import var, NoDefault
from paste.util.template import paste_script_template_renderer

class MakeZopeApp(templates.BasicPackage):
    _template_dir = 'make_zope_app'
    summary = 'Package that contains a Zope application'
    required_templates = []
    vars = []

class DeployZopeApp(templates.Template):
    _template_dir = 'deploy_zope_app'
    summary = 'Deploy a Zope application'
    required_templates = []
    vars = [
        var('user', 'Name of an initial administrator user', default=NoDefault),
        var('passwd', 'Password for the initial administrator user',
            default=NoDefault),
        ]

    template_renderer = staticmethod(paste_script_template_renderer)

    def check_vars(self, vars, cmd):
        vars = super(DeployZopeApp, self).check_vars(vars, cmd)
        project = vars['project']
        if (os.path.isdir(project) and
            os.path.isfile(os.path.join(project, 'setup.py'))):
            vars['develop'] = '.'
        else:
            vars['develop'] = ''
        return vars

def make_zope_app():
    extra_args = sys.argv[1:]
    command.run(['create', '-t', 'make_zope_app'] + extra_args)

def deploy_zope_app():
    extra_args = sys.argv[1:]
    command.run(['create', '-t', 'deploy_zope_app'] + extra_args)
