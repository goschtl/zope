import os

from pkg_resources import Requirement
from zc.buildout.easy_install import scripts
from zc.recipe.egg import Egg
from zc.recipe.testrunner import TestRunner
from zope.kgs import kgs


class Recipe(object):
    """Recipe for z3c.recipe.kgs"""

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.packages = options.get('packages')
        self.script = options.get('script', self.name)
        self.max_jobs = options.get('max_jobs', 1)
        self.kgs = kgs.KGS(options['kgs'])

    def install(self):
        return self.update()

    def update(self):
        runners = []
        installed = []
        # loop on the packages from the KGS
        for package in self.kgs.packages:
            # skip the package if it is marked as "not tested" or
            # if it is not in the list "packages", if defined
            if not package.tested or \
               self.packages is not None and \
               package.name not in self.packages:
                continue
            # get the extra and test dependencies
            eggs = Egg(self.buildout, self.name, dict(
                eggs='%s == %s' % (package.name, package.versions[-1])
            ))
            working_set = eggs.working_set()[1]
            extras = working_set.find(Requirement.parse(package.name)).extras
            # install the test runner for the package
            options = dict(eggs="%s [%s] == %s" % (
                package.name, ','.join(extras), package.versions[-1],
            ))
            name = '%s-%s' % (self.name, package.name)
            recipe = TestRunner(self.buildout, name, options)
            runners.append(repr(os.path.join(
                self.buildout['buildout']['bin-directory'], name)))
            installed.extend(recipe.install())
        # install the KGS test runner
        eggs = Egg(self.buildout, self.name, dict(eggs='z3c.recipe.kgs'))
        working_set = eggs.working_set()[1]
        installed.extend(scripts(
            [(self.script, 'z3c.recipe.kgs.runner', 'main')], working_set,
            self.buildout['buildout']['executable'],
            self.buildout['buildout']['bin-directory'],
            arguments='%s,\n        ' % self.max_jobs + \
                ',\n        '.join(runners) + '\n    ')
        )
        # return the list of installed recipes
        return installed


