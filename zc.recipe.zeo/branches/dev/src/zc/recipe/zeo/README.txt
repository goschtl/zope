Creating ZEO Instances
**********************

Note that at this time, the recipe is unix-centric.  We'll add windows
support in the future.

The ZEO instance recipe (zc.recipe.zeoinstance) creates a ZEO
instance. It takes a number of options:

zeo
   An distribution requirement for a distribution providing ZEO
   software. This currently defaults to ZODB3.

zdaemon
   An distribution requirement for a distribution providing zdaemon
   software. This currently defaults to ZODB3.

database
   The name of a section that has a zconfig option providing a
   database definition.

options
   A collection of ZEO ZConfig options.  These are given as name-value
   pairs on separate lines.

The recipe also supports the options defined by the zc.recipe.eggs
recipe with the exception of the eggs, scripts, entry-points, and
extra-paths options.

Let's look at a basic example.  We'll define a ZEO instace named
'storage':

    >>> write("buildout.cfg",
    ... '''
    ... [buildout]
    ... parts = storage
    ... 
    ... [foo]
    ... zconfig =
    ...    <zodb>
    ...       <filestorage>
    ...           path = /var/foo/Data.fs
    ...       </filestorage>
    ...    </zodb>
    ...
    ... [storage]
    ... recipe = zc.recipe.zeo
    ... database = foo
    ...
    ... ''')

Note that in this case, we provided a database section with an
explicit zconfig option.  Usually, we'll use another recipe, like the
zc.recipe.filestorage recipe to define a database.

If we run the buildout, we'll get a storage part:

    >>> print system(join('bin', 'buildout')),
    buildout: Installing storage

    >>> ls('parts', 'storage')
    -  runzeo
    -  zdrun
    -  zeo.conf

    >>> cat('parts', 'storage', 'zeo.conf')
    # ZEO configuration file
    #
    # This file is generated.  If you edit this file, your edits could
    # easily be lost.
    <BLANKLINE>
    <zeo>
      address 8100
    </zeo>
    <BLANKLINE>
    <filestorage 1>
    path = /var/foo/Data.fs
    </filestorage>
    <BLANKLINE>
    <BLANKLINE>
    <eventlog>
      level info
      <logfile>
        path /sample-buildout/parts/storage/zeo.log
      </logfile>
    </eventlog>
    <BLANKLINE>
    <runner>
      program /sample-buildout/parts/storage/runzeo
      socket-name /sample-buildout/parts/storage/zeo.zdsock
      daemon true
      forever false
      backoff-limit 10
      exit-codes 0, 2
      directory /sample-buildout/parts/storage
      default-to-interactive true
      python /usr/local/bin/python2.4
      logfile /sample-buildout/parts/storage/zeo.log
    </runner>

    >>> cat('parts', 'storage', 'zdrun')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/eggs/ZODB3-3.7.0-py2.4-linux-i686.egg',
      ]
    <BLANKLINE>
    import zdaemon.zdrun
    <BLANKLINE>
    if __name__ == '__main__':
        zdaemon.zdrun.main()

    >>> cat('parts', 'storage', 'runzeo')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/eggs/ZODB3-3.7.0-py2.4-linux-i686.egg',
      ]
    <BLANKLINE>
    import ZEO.runzeo
    <BLANKLINE>
    if __name__ == '__main__':
        ZEO.runzeo.main(
            ["-C", '/sample-buildout/parts/storage/zeo.conf']
            + sys.argv[1:])

We also get a storage script in the buildout bin directory:

    >>> cat('bin', 'storage')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/eggs/ZODB3-3.7.0-py2.4-linux-i686.egg',
      ]
    <BLANKLINE>
    import ZEO.zeoctl
    <BLANKLINE>
    if __name__ == '__main__':
        ZEO.zeoctl.main(
            ["-C", '/sample-buildout/parts/storage/zeo.conf']
            + sys.argv[1:])

The zeo recipe also produces a zconfig option that can be used by
other recipes.  To see this, we'll create a recipe that that outputs
the zconfig option produced for the storage:

    >>> mkdir('recipes')
    >>> write('recipes', 'setup.py', 
    ... '''
    ... from setuptools import setup
    ... setup(name='recipes',
    ...       entry_points={'zc.buildout': ['showconfig = showconfig:Recipe']},
    ...       )
    ... ''')

    >>> write('recipes', 'showconfig.py',
    ... '''
    ... class Recipe:
    ...     def __init__(self, buildout, name, options):
    ...         print buildout['storage']['zconfig']
    ...     def install(self):
    ...         return ()
    ...     def update(self):
    ...         pass
    ... ''')

    >>> write("buildout.cfg",
    ... '''
    ... [buildout]
    ... develop = recipes
    ... parts = storage showconfig
    ... 
    ... [foo]
    ... zconfig =
    ...    <zodb>
    ...       <filestorage>
    ...           path = /var/foo/Data.fs
    ...       </filestorage>
    ...    </zodb>
    ...
    ... [storage]
    ... recipe = zc.recipe.zeo
    ... database = foo
    ...
    ... [showconfig]
    ... recipe = recipes:showconfig
    ... ''')

    >>> print system(join('bin', 'buildout')),
    buildout: Develop: /sample-buildout/recipes/setup.py
    <zodb>
      <zeoclient>
         server 8100
      </zeoclient>
    </zodb>
    <BLANKLINE>
    buildout: Updating storage
    buildout: Installing showconfig
