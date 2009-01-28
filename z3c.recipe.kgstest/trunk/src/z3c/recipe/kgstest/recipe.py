import os
import pkg_resources
import popen2
import re
import zc.buildout.easy_install
import zc.recipe.egg
import zc.recipe.testrunner


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
INCLUDE = ['zope.*', 'grokcore.*']


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
        self.include = string2list(self.options.get('include', ''), INCLUDE)

    def install(self):
        return self.update()

    def update(self):
        files = []
        for project in self._wanted_projects():
            if self._needs_test_dependencies(project):
                extra = ' [test]'
            else:
                extra = ''
            options = dict(eggs=project + extra)
            recipe = zc.recipe.testrunner.TestRunner(
                self.buildout, '%s-%s' % (self.name, project), options)
            files.extend(recipe.install())
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
            for regex in self.include:
                if re.compile(regex).search(project):
                    skip = False
                    break
            if not skip:
                projects.append(project)
        return projects

    def _needs_test_dependencies(self, package):
        options = dict(eggs=package)
        saved_newest = self.buildout['buildout'].get('newest', None)
        self.buildout['buildout']['newest'] = 'true'
        eggs = zc.recipe.egg.Egg(self.buildout, self.name, options)
        _, ws = eggs.working_set()
        latest = ws.find(pkg_resources.Requirement.parse(package))
        if saved_newest:
            self.buildout['buildout']['newest'] = saved_newest
        return 'test' in latest.extras
