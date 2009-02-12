import sys
import os.path
import shutil
from ConfigParser import ConfigParser
from paste.script.templates import var, NoDefault, Template, BasicPackage

HOME = os.path.expanduser('~')

def get_buildout_default_eggs_dir():
    default_cfg = os.path.join(HOME, '.buildout', 'default.cfg')
    if os.path.isfile(default_cfg):
        cfg = ConfigParser()
        cfg.read(default_cfg)
        if cfg.has_option('buildout', 'eggs-directory'):
            eggs_dir = cfg.get('buildout', 'eggs-directory').strip()
            if eggs_dir:
                return os.path.expanduser(eggs_dir)

def default_eggs_dir():
    buildout_default = get_buildout_default_eggs_dir()
    if buildout_default:
        return buildout_default
    return os.path.join(HOME, 'buildout-eggs')

class ZopeDeploy(Template):
    _template_dir = 'zope_deploy'
    summary = "(Paste) deployment of a Zope application"

    vars = [
        var('user', 'Name of an initial administrator user', default=NoDefault),
        var('passwd', 'Password for the initial administrator user',
            default=NoDefault),
        var('eggs_dir', 'Location where zc.buildout will look for and place '
            'packages', default=default_eggs_dir())
        ]

    def check_vars(self, vars, cmd):
        vars = super(ZopeDeploy, self).check_vars(vars, cmd)
        buildout_default = get_buildout_default_eggs_dir()
        input = os.path.expanduser(vars['eggs_dir'])
        if input == buildout_default:
            vars['eggs_dir'] = ('# eggs will be installed in the default '
                                'buildout location\n'
                                '# (see ~/.buildout/default.cfg)')
        else:
            vars['eggs_dir'] = 'eggs-directory = %s' % input
        return vars

class ZopeApp(Template):
    _template_dir = 'zope_app'
    summary = 'Package that contains a Zope application'
    required_templates = ['zope_deploy']
