import os, re

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

    def install(self):
        options = self.options
        location = options['location']
        if os.path.exists(location):
            if self.buildout['buildout'].get('offline') == 'true':
                return location
            os.chdir(location)
            i, o = os.popen4('svn up -r %s' % options['revision'])
            i.close()
            change = re.compile('[ADUCM] ').match
            for l in o:
                if change(l):
                    o.read()
                    o.close()
                    break
                else:
                    # No change, so all done
                    o.close()
                    return location
        else:
            assert os.system('svn co -r %s %s %s' % (
                options['revision'], options['url'], location)) == 0
            os.chdir(location)

        assert os.spawnl(
            os.P_WAIT, options['executable'], options['executable'],
            'setup.py',
            'build_ext', '-i',
            'install_data', '--install-dir', '.',
            ) == 0

        return location
