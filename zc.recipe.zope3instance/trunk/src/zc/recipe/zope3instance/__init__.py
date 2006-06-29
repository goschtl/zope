import os, re, shutil
import zc.buildout
import zc.recipe.egg

class Recipe(zc.recipe.egg.Egg):
    # Need to think about the inheritence interface
    # it *is* reasonable to think about instances as an
    # extension of the basic egg/script-generation model.

    def __init__(self, buildout, name, options):
        zc.recipe.egg.Egg.__init__(self, buildout, name, options)

        options['zope3'] = options.get('zope3', 'zope3')
        options['database-config'] = buildout[options['database']]['zconfig']
        python = buildout['buildout']['python']
        options['zope3-directory'] = buildout[options['zope3']]['location']
        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name,
            )
        options['scripts'] = '' # suppress script generation.

    def install(self):
        
        options = self.options
        location = options['location']
        if os.path.exists(location):
            return location

        # Gather information on extra distros. We should be able to
        # inherit the next 2 statements, but Egg doesn't provide a
        # subclassing api
        
        distributions = [
            r.strip()
            for r in options.get('distribution', self.name).split('\n')
            if r.strip()
            ]

        if self.buildout['buildout'].get('offline') == 'true':
            ws = zc.buildout.easy_install.working_set(
                distributions, options['executable'],
                [options['_d'], options['_e']]
                )
        else:
            ws = zc.buildout.easy_install.install(
                distributions, options['_e'],
                links = self.links,
                index = self.index, 
                executable = options['executable'],
                always_unzip=options.get('unzip') == 'true',
                path=[options['_d']]
                )
        
        # What follows is a bit of a hack because the instance-setup mechanism
        # is a bit monolithic.  We'll run mkzopeinstabce and then we'll
        # patch the result.  A better approach might be to provide independent
        # instance-creation logic, but this raises lots of issues that
        # need to be stored out first.
        mkzopeinstance = os.path.join(options['zope3-directory'],
                                      'bin', 'mkzopeinstance')

        assert os.spawnl(
            os.P_WAIT, options['executable'], options['executable'],
            mkzopeinstance, '-d', location, '-u', options['user'],
            '--non-interactive',
            ) == 0

        try:

            # Now, patch the zodb option in zope.conf
            zope_conf_path = os.path.join(location, 'etc', 'zope.conf')
            zope_conf = open(zope_conf_path).read()
            zope_conf = (
                zope_conf[:zope_conf.find('<zodb>')]
                +
                options['database-config']
                +
                zope_conf[zope_conf.find('</zodb>')+7:]
                )
            open(zope_conf_path, 'w').write(zope_conf)

            # Patch extra paths into binaries
            path = "\n        '" + "',\n        '".join([
                dist.location for dist in ws]) + "'\n        "
            for script_name in 'runzope', 'debugzope', 'scriptzope':
                script_path = os.path.join(location, 'bin', script_name)
                script = open(script_path).read()
                # don't look :/
                script = script.replace(
                    'sys.path[:] = [',
                    'sys.path[:] = ['+path+'] + ['
                    )
                open(script_path, 'w').write(script)

            # finally, add zcml files to package-includes
            zcml = options.get('zcml')
            if zcml:
                includes_path = os.path.join(
                    location, 'etc', 'package-includes')
                zcml = zcml.split()
                if '*' in zcml:
                    zcml.remove('*')
                else:
                    shutil.rmtree(includes_path)
                    os.mkdir(includes_path)

                n = 0
                package_match = re.compile('\w+([.]\w+)*$').match
                for package in zcml:
                    n += 1
                    orig = package
                    if ':' in package:
                        package, filename = package.split(':')
                    else:
                        filename = None

                    if '-' in package:
                        package, suff = package.split('-')
                        if suff not in ('configure', 'meta', 'overrides'):
                            raise ValueError('Invalid zcml', orig)
                    else:
                        suff = 'configure'

                    if filename is None:
                        filename = suff + '.zcml'

                    if not package_match(package):
                        raise ValueError('Invalid zcml', orig)

                    path = os.path.join(
                        includes_path,
                        "%3.3d-%s-%s.zcml" % (n, package, suff),
                        )
                    open(path, 'w').write(
                        '<include package="%s" file="%s" />\n'
                        % (package, filename)
                        )
                    
        except:
            # clean up
            shutil.rmtree(location)
            raise
        
        return location
