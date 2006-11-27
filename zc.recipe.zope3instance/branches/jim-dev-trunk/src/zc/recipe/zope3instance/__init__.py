import os, re, shutil
import zc.buildout
import zc.recipe.egg

class Recipe:
    # Need to think about the inheritence interface
    # it *is* reasonable to think about instances as an
    # extension of the basic egg/script-generation model.

    def __init__(self, buildout, name, options):
        self.egg = zc.recipe.egg.Egg(buildout, name, options)
        self.options, self.name = options, name

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

        requirements, ws = self.egg.working_set()

        if os.path.exists(location):

            # See is we can stop.  We need to see if the working set path
            # has changed.
            saved_path_path = os.path.join(location, 'etc', '.eggs')
            if os.path.isfile(saved_path_path):
                if (open(saved_path_path).read() ==
                    '\n'.join([d.location for d in ws])
                    ):
                    return location

            # The working set has changed.  Blow away the instance.
            shutil.rmtree(location)
        
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
            # Save the working set:
            open(os.path.join(location, 'etc', '.eggs'), 'w').write(
                '\n'.join([d.location for d in ws]))

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
