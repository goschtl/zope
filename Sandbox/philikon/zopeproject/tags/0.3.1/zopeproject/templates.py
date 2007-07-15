import sys
import os.path
import shutil
from paste.script.templates import var, NoDefault, Template, BasicPackage

HOME = os.path.expanduser('~')

class ZopeDeploy(Template):
    _template_dir = 'zope_deploy'
    summary = "(Paste) deployment of a Zope application"

    vars = [
        var('user', 'Name of an initial administrator user', default=NoDefault),
        var('passwd', 'Password for the initial administrator user',
            default=NoDefault),
        var('eggs_dir', 'Location where zc.buildout will look for and place '
            'packages', default=os.path.join(HOME, 'buildout-eggs'))
        ]

    def check_vars(self, vars, cmd):
        vars = super(ZopeDeploy, self).check_vars(vars, cmd)
        vars['eggs_dir'] = os.path.expanduser(vars['eggs_dir'])
        return vars

class ZopeApp(Template):
    _template_dir = 'zope_app'
    summary = 'Package that contains a Zope application'
    required_templates = ['zope_deploy']
