import sys
from paste.script import templates, command

class ZopeApp(templates.BasicPackage):
    _template_dir = 'template'
    summary = 'Package that contains a Zope application'
    required_templates = []
    vars = []

def main():
    extra_args = sys.argv[1:]
    command.run(['create', '-t', 'zope_app'] + extra_args)
