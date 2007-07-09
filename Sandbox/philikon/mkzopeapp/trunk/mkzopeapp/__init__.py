import sys
from paste.script import templates, command

class MakeZopeApp(templates.BasicPackage):
    _template_dir = 'make_zope_app'
    summary = 'Package that contains a Zope application'
    required_templates = []
    vars = []

def make_zope_app():
    extra_args = sys.argv[1:]
    command.run(['create', '-t', 'make_zope_app'] + extra_args)
