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
INCLUDE = ['^zope\..*', '^grokcore\..*']


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

        self.script = self.options.get('script', 'test-compat')
        self.wanted_packages = self._wanted_packages()

    def install(self):
        return self.update()

    def update(self):
        installed = []
        installed.extend(self._install_testrunners())
        installed.extend(self._install_run_script())
        return installed

    def _install_testrunners(self):
        installed = []
        for package in self.wanted_packages:
            if self._needs_test_dependencies(package):
                extra = ' [test]'
            else:
                extra = ''
            options = dict(eggs=package + extra)
            recipe = zc.recipe.testrunner.TestRunner(
                self.buildout, '%s-%s' % (self.name, package), options)
            installed.extend(recipe.install())
        return installed

    def _install_run_script(self):
        bindir = self.buildout['buildout']['bin-directory']
        runners = ['%s-%s' % (self.name, package) for package
                        in self.wanted_packages]
        runners = [repr(os.path.join(bindir, runner)) for runner in runners]

        return zc.buildout.easy_install.scripts(
            [(self.script, 'z3c.recipe.compattest.runner', 'main')],
            self._working_set('z3c.recipe.compattest'),
            self.buildout['buildout']['executable'],
            bindir, arguments = '%s' % ', '.join(runners))

    def _wanted_packages(self):
        projects = []
        svn_list, _ = popen2.popen2("svn ls %s" % self.svn_url)
        for project in svn_list:
            project = project[:-2]
            include = False
            for regex in self.include:
                if re.compile(regex).search(project):
                    include = True
                    break
            for regex in self.exclude:
                if re.compile(regex).search(project):
                    include = False
                    break
            if include:
                projects.append(project)
        return projects

    def _needs_test_dependencies(self, package):
        ws = self._working_set(package)
        package = ws.find(pkg_resources.Requirement.parse(package))
        return 'test' in package.extras

    def _working_set(self, package):
        eggs = zc.recipe.egg.Egg(self.buildout, self.name, dict(eggs=package))
        _, ws = eggs.working_set()
        return ws
