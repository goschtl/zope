from paste.script import templates
from paste.script.templates import var

class BlueBream(templates.Template):

    _template_dir = 'project_template'
    summary = "A Zope project"
    vars = [var('namespace_package', '')]

