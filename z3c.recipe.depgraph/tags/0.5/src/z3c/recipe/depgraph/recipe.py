import os
import re

from zc.buildout import easy_install
from zc.recipe.egg import Egg

EXCLUDE_PACKAGES = set((
    'lxml',
    'pytz',
    'setuptools',
    'tl.eggdeps',
    'z3c.recipe.depgraph',
    'zc.buildout',
    'zc.recipe.egg',
))


class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.egg = Egg(buildout, options['recipe'], options)
        self.eggs = self.options.get('eggs', '').split('\n')
        self.strict = self.options.get('strict', '').lower() in ('1', 'true', 'yes')

        exclude = self.options.get('exclude', '')
        re_exclude = self.options.get('re-exclude', '')
        dead_ends = self.options.get('dead-ends', '')
        re_dead_ends = self.options.get('re-dead-ends', '')

        self.exclude = set(exclude.split())
        self.re_exclude = set(re_exclude.split())
        self.dead_ends = set(dead_ends.split())
        self.re_dead_ends = set(re_dead_ends.split())

        self.output = self.options.get(
            'output', os.path.join(
                self.buildout['buildout']['parts-directory'], self.name))
        extras = self.options.get('extras', 'false')
        self.extras = extras.lower() in ('1', 'true', 'yes')
        self.formats = self.options.get('formats', 'svg').split()

    def install(self):
        options = self.options
        reqs, ws = self.egg.working_set(['z3c.recipe.depgraph'])

        if not os.path.exists(self.output):
            os.mkdir(self.output)

        variants = options.get('variants', 'base tred scc')
        variants = [v.strip() for v in variants.split()]


        def matcher(names, patterns):
            names = set(names)
            matched_names = set()
            compiled_patterns = [re.compile(pattern) for pattern in patterns]

            def match(name, compiled_patterns):
                for pattern in compiled_patterns:
                    if pattern.search(name):
                         # matching one pattern is sufficient
                        matched_names.add(name)
                        return

            for name in names:
                match(name, compiled_patterns)
            return matched_names

        if self.strict:
            # use only eggs in the list
            packages = self.eggs

        else:
            # Install an interpreter to find eggs
            packages = set([dist.project_name for dist in ws.by_key.values()])
            # Remove eggs listed in exclude option
            packages = packages - EXCLUDE_PACKAGES - self.exclude
            # Remove eggs listed in re-exclude option
            packages = packages - matcher(packages, self.re_exclude)
            packages = list(packages)

        # Allow to map distribution names to different package names
        pmap = dict()
        package_map = options.get('package-map', '').strip()
        if package_map:
            pmap = self.buildout[package_map]
        packages.sort()

        easy_install.scripts(
            [('graph-%s' % self.name, 'z3c.recipe.depgraph.runner', 'main')],
            ws, options['executable'], options['bin-directory'],
            arguments=dict(
                packages=packages,
                package_map=package_map,
                name=self.name,
                path=self.output,
                variants=variants,
                formats=self.formats,
                extras=self.extras,
                exclude = self.exclude,
                re_exclude = self.re_exclude,
                dead_ends = self.dead_ends,
                re_dead_ends = self.re_dead_ends
                ),
        )

        reqs = ['tl.eggdeps']
        scripts = {
            'eggdeps' : '%s-eggdeps' % self.name
        }

        easy_install.scripts(
            reqs, ws, options['executable'], options['bin-directory'],
            scripts=scripts,
        )
        return self.output

    def update(self):
        self.install()
