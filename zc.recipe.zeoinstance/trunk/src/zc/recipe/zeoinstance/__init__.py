import os, re, shutil
import zc.buildout

start_section = re.compile('(^|\n)[ \t]*<[^>]+>[ \t]*\n').search
end_section = re.compile('(^|\n)[ \t]*</[^>]+>[ \t]*\n').search

class Recipe:
    # Need to think about the inheritence interface
    # it *is* reasonable to think about instances as an
    # extension of the basic egg/script-generation model.

    def __init__(self, buildout, name, options):
        self.options, self.name = options, name

        options['zeo'] = options.get('zeo', 'zeo')
        self._getdbconfig(buildout, options)
        python = buildout['buildout']['python']
        options['zeo-directory'] = buildout[options['zeo']]['location']
        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name,
            )
        python = buildout['buildout']['python']
        options['executable'] = buildout[python]['executable']
        options['port'] = options.get('port', '8100')
        options['zconfig'] = zeoclient_tempalte % options['port']

    def _getdbconfig(self, buildout, options):
        dbconfig = buildout[options['database']]['zconfig']
        #import pdb; pdb.set_trace()
        dbconfig = dbconfig[start_section(dbconfig).end(0):]
        dbconfig = dbconfig[start_section(dbconfig).start(0):]
        dbconfig = dbconfig[:end_section(dbconfig).end(0):]
        dbconfig = dbconfig.replace('>', ' 1>', 1)
        options['database-config'] = dbconfig

    def install(self):
        
        options = self.options
        location = options['location']

        if os.path.exists(location):
            return location
        
        # What follows is a bit of a hack because the instance-setup mechanism
        # is a bit monolithic.  We'll run mkzeoinstabce and then we'll
        # patch the result.  A better approach might be to provide independent
        # instance-creation logic, but this raises lots of issues that
        # need to be stored out first.
        mkzeoinstance = os.path.join(options['zeo-directory'],
                                      'bin', 'mkzeoinstance')

        assert os.spawnl(
            os.P_WAIT, options['executable'], options['executable'],
            mkzeoinstance, location,
            ) == 0

        try:
            # Now, patch the zodb option in zeo.conf
            zeo_conf_path = os.path.join(location, 'etc', 'zeo.conf')
            zeo_conf = open(zeo_conf_path).read()
            zeo_conf = zeo_conf.replace('address 8100',
                                        'address %s' % options['port'],
                                        1)
            zeo_conf = (
                zeo_conf[:zeo_conf.find('<filestorage 1>')]
                +
                options['database-config']
                +
                zeo_conf[zeo_conf.find('</filestorage>')+15:]
                )
            open(zeo_conf_path, 'w').write(zeo_conf)

                    
        except:
            # clean up
            shutil.rmtree(location)
            raise
        
        return location

    def update(self):
        pass

zeoclient_tempalte = """\
<zodb>
  <zeoclient>
     server localhost:%s
  </zeoclient>
</zodb>
"""
