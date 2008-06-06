import sys, os, pkg_resources, subprocess

import distutils.core
import setuptools.command.easy_install
import zc.buildout.easy_install
import zc.recipe.egg

ei_logger = zc.buildout.easy_install.logger

class Setup(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

    def install(self):
        setups = [os.path.join(self.buildout['buildout']['directory'],
                               setup.strip())
                  for setup in self.options['setup'].split('\n')
                  if setup.strip()]
        if 'args' in self.options:
            for setup in setups:
                self.buildout.setup(
                    [setup] + self.options['args'].split())

        if self.options.get('develop') == 'true':
            develop(self, setups)
        
        return ()

    update = install

class Editable(zc.recipe.egg.Eggs):

    def __init__(self, buildout, name, options):
        super(Editable, self).__init__(buildout, name, options)
        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'], self.name)
        if 'build-directory' not in options:
            options['build-directory'] = options['location']
        else:
            options['build-directory'] = os.path.join(
                buildout['buildout']['directory'], 
                options['build-directory'])

        self.reqs = [
            pkg_resources.Requirement.parse(r.strip())
            for r in options.get('eggs', self.name).split('\n')
            if r.strip()]

        self.newest = buildout['buildout'].get('newest') == 'true'
        self.online = (self.newest and
                       buildout['buildout'].get('offline') != 'true')

        # Track versions
        if self.online:
            options['versions'] = self.get_online_versions()
        else:
            options['versions'] = self.get_offline_versions()
            
    def install(self):
        if not self.online:
            return self.get_location()
        
        options = self.options

        dists = [req.unsafe_name for req in self.reqs if not
                 os.path.isdir(os.path.join(
                    self.options['build-directory'], req.key))]
        if len(dists) > 0:
            args = ['-c', zc.buildout.easy_install._easy_install_cmd]
            
            if options.get('unzip') == 'true':
                args += ['-Z']
            level = ei_logger.getEffectiveLevel()
            if level > 0:
                args += ['-q']
            elif level < 0:
                args += ['-v']

            args.extend(
                ['--find-links='+' '.join(self.links), '--editable',
                 '--build-directory='+options['build-directory']])
            args.extend(dists)
            path = self.installer._get_dist(
                pkg_resources.Requirement.parse('setuptools'),
                pkg_resources.WorkingSet([]), False,)[0].location
            sys.stdout.flush() # We want any pending output first
            sys.stderr.flush()
            ei_logger.debug(
                'Running easy_install:\n%s "%s"\npath=%s\n',
                options['executable'], '" "'.join(args), path)
            returncode = subprocess.Popen(
                args=[options['executable']]+args,
                env=dict(os.environ, PYTHONPATH=path)
                ).wait()
            assert returncode == 0, (
                'easy_install exited with returncode %s' % returncode)
        
        if self.options.get('develop') == 'true':
            develop(self, (
                    os.path.join(self.options['build-directory'],
                                 req.key)
                    for req in self.reqs))

        return self.get_location()

    update = install

    def get_location(self):
        if os.path.isdir(self.options['location']):
            return self.options['location']
        else:
            return ()

    def get_online_versions(self):
        options = self.options
        self.installer = zc.buildout.easy_install.Installer(
            links=self.links,
            index = self.index, 
            executable = options['executable'],
            always_unzip=options.get('unzip') == 'true',
            path=[options['develop-eggs-directory']],
            newest=self.newest)
        return '\n'.join([
                '%s==%s' % (dist.project_name, dist.version)
                for dist in (self.installer._obtain(req, source=True)
                             for req in self.reqs)
                if dist is not None])

    def get_offline_versions(self):
        options = self.options
        return '\n'.join([
                '%s==%s' % (dist.get_name(), dist.get_version())
                for dist in (
                    distutils.core.run_setup(
                        os.path.join(options['build-directory'],
                                     req.key, 'setup.py'),
                        stop_after='commandline')
                    for req in self.reqs
                    if os.path.isdir(
                        os.path.join(options['build-directory'],
                                     req.key)))])

def develop(self, setups):
    for setup in setups:
        self.buildout._logger.info("Develop: %r", setup)
        zc.buildout.easy_install.develop(
            setup=setup, dest=self.buildout['buildout'][
                'develop-eggs-directory'])
