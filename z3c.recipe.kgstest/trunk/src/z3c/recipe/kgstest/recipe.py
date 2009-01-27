import os
import popen2
import re


EXCLUDE = ['zope.agxassociation', 'zope.app.css', 'zope.app.demo', \
           'zope.app.fssync', 'zope.app.recorder', \
           'zope.app.schemacontent', 'zope.app.sqlexpr', \
           'zope.app.styleguide', 'zope.app.tests', \
           'zope.app.versioncontrol', 'zope.app.zopetop', \
           'zope.bobo', 'zope.browserzcml2', 'zope.fssync', \
           'zope.generic', 'zope.importtool', 'zope.kgs', \
           'zope.release', 'zope.pytz', 'zope.timestamp', \
           'zope.tutorial', 'zope.ucol', 'zope.weakset', \
           'zope.webdev', 'zope.xmlpickle', 'zope.app.boston',]


def string2list(string, default):
    result = string and string.split('\n') or default
    return [item.strip() for item in result]


class Recipe(object):
    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        self.svn_url = self.options.get('svn_url',
                                        'svn://svn.zope.org/repos/main/')
        self.exclude = string2list(self.options.get('exclude', ''), EXCLUDE)
        self.include = string2list(self.options.get('include', ''), [])

    def install(self):
        files = []
        for project in self._wanted_projects():
            testrunner = os.path.join(self.buildout['buildout']['bin-directory'],
                                      'kgstest-%s' % project)
            open(testrunner, 'w').write('foo')
            files.append(testrunner)
        return files

    def _wanted_projects(self):
        projects = []
        svn_list, _ = popen2.popen2("svn ls %s" % self.svn_url)
        for project in svn_list:
            project = project[:-2]
            skip = False
            for regex in self.exclude:
                if re.compile(regex).search(project):
                    skip = True
                    break
            if skip:
                continue
            parts = project.split('.')
            if parts[0] in ('zope', 'grokcore', ):
                projects.append(project)
        projects.extend(self.include)
        return projects

    def update(self):
        return []
