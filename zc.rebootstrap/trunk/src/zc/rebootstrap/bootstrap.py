
import os, pkg_resources

class Recipe:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        options['dest'] = os.path.join(
            buildout['buildout']['bin-directory'],
            self.name)

    def install(self):
        loc = pkg_resources.working_set.find(
            pkg_resources.Requirement.parse('setuptools')
            ).location
        fname = os.path.basename(loc)
        dest = self.options['dest']
        open(dest, 'w').write(
            template % os.path.join('eggs', fname)
            )
        return dest

    def update(self):
        pass

template = """
import sys
sys.path.insert(0, 'eggs')
sys.path.insert(0, %r)
import pkg_resources
pkg_resources.require('zc.buildout')
import zc.buildout.buildout

zc.buildout.buildout.main(sys.argv[1:] + ['bootstrap'])
"""
