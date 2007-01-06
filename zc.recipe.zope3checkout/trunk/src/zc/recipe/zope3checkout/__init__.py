import os, re

SVN_WORKINGDIR_CHANGED = re.compile('[ADUCM] ').match


class Recipe:

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        python = buildout['buildout']['python']
        options['executable'] = buildout[python]['executable']
        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name)
        options.setdefault('revision', 'HEAD')

        self.revision = options.get('revision')
        self.location = options['location']
        self.url = options['url']
        self.executable = options['executable']

    def update(self):
        """Update the Zope 3 checkout.

        Does nothing if buildout is in offline mode.

        """
        if self.buildout['buildout'].get('offline') == 'true':
            return self.location

        os.chdir(self.location)
        stdin, stdout = os.popen4('svn up -r %s' % self.revision)
        stdin.close()
        changed = False
        for line in stdout:
            if SVN_WORKINGDIR_CHANGED(line):
                changed = True
                break
        # XXX kept after refactoring. I don't know whether this
        # is really needed.
        stdout.read()
        stdout.close()

        if changed:
            self._compile()
        return self.location

    def install(self):
        """Checkout a Zope 3 working copy.

        Fails if buildout is running in offline mode.

        """
        assert os.system('svn co -r %s %s %s' % (
            self.revision, self.url, self.location)) == 0
        self._compile()
        return self.location

    def _compile(self):
        os.chdir(self.location)
        assert os.spawnl(
            os.P_WAIT, self.executable, self.executable,
            'setup.py',
            'build_ext', '-i',
            'install_data', '--install-dir', '.',
            ) == 0
