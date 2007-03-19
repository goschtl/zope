import os
import logging
import zc.buildout
import zc.recipe.egg

server_types = {
    # name     (module,                  http-name)
    'twisted': ('zope.app.twisted.main', 'HTTP'),
    'zserver': ('zope.app.server.main',  'WSGI-HTTP'),
    }


class Application(object):

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        wd = options.get('working-directory', '')
        if not wd:
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'], name)

        options['bin-directory'] = buildout['buildout']['bin-directory']
        options['run-directory'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name,
            )

        options['servers'] = options.get('servers', 'twisted')
        if options['servers'] not in server_types:
            raise ValueError(
                'servers setting must be one of "twisted" or "zserver"')

        options['scripts'] = ''
        self.egg = zc.recipe.egg.Egg(buildout, name, options)
        
    def install(self):
        options = self.options
        dest = []
        wd = options.get('working-directory', '')
        if not wd:
            wd = options['location']
            if os.path.exists(wd):
                assert os.path.isdir(wd)
            else:
                os.mkdir(wd)
            dest.append(wd)
        fd = open(os.path.join(wd, 'site.zcml'), 'w')
        fd.write(options['site.zcml'])
        fd.close()


        self.egg.install()
        requirements, ws = self.egg.working_set()

        # install subprograms and ctl scripts
        server_module = server_types[options['servers']][0]
        zc.buildout.easy_install.scripts(
            [('runzope', server_module, 'main')],
            ws, options['executable'], wd,
            )

        return dest

    def update(self):
        pass
