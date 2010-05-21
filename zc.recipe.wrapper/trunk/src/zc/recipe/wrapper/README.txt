zc.recipe.wrapper
=================

One of the goals to using buildout is to avoid changing the system in order to
develop.  Another goal is to generate the ancillary scripts necessary for
testing and administration and ensure that they use the same version of all
dependancies in dev and stage enviroments as production environments.
Unfortunately in the case of dynamic libraries, the former goal works against
the latter goal, because the generated scripts will not include the
appropriate libraries at the start of the python interpreter, which is
necessary to access external libraries using ctypes (essential for some
libraries, such as lcms), and OS X compatibility.  zc.recipe.wrapper aims to
solve this by providing a generic interface to create wrapper scripts.

Basic Use
---------

To start off, lets create a buildout that generates a python interpreter,
called `py`.

    >>> import os
    >>> buildout = setupBuildout(sample_buildout, "buildout.cfg",
    ... """
    ... [buildout]
    ... parts = interpreter
    ... versions = versions
    ... develop = %s
    ...
    ... [versions]
    ... zc.recipe.egg = 1.0.0
    ... setuptools = 0.6c11
    ... zc.recipe.testrunner = 1.0.0
    ... zc.buildout = 1.0.0
    ... zope.testing = 3.5.0
    ...
    ... [interpreter]
    ... recipe = zc.recipe.egg
    ... eggs = zc.recipe.wrapper
    ... interpreter = py
    ... """ % wrapper)
    >>> os.chdir(sample_buildout)
    >>> buildout.install([])
    Develop: '...'
    Installing interpreter.
    Getting distribution for 'zope.testing==3.5.0'.
    Got zope.testing 3.5.0.
    Getting distribution for 'zc.recipe.testrunner==1.0.0'.
    Got zc.recipe.testrunner 1.0.0.
    Getting distribution for 'zc.recipe.egg==1.0.0'.
    Got zc.recipe.egg 1.0.0.
    Generated interpreter 'PREFIX/bin/py'.
    >>> buildout_pprint(dict(buildout))
    {'buildout': {...},
     'interpreter': {...
                     'interpreter': 'py',
                     'recipe': 'zc.recipe.egg'},
     'versions': {...}}
    >>> print ls(os.path.join(sample_buildout, 'bin/py'))
    -rwxr-xr-x USER GROUP PREFIX/bin/py
    >>> print ls(os.path.join(sample_buildout, 'bin/basepy'))
    Traceback (most recent call last):
        ...
    OSError: [Errno 2] No such file or directory: '/.../sample-buildout/bin/basepy'
    >>> os.chdir(wrapper)

We might desire to run `py` with an addition to the dynamic load path:

    >>> buildout = setupBuildout(sample_buildout, "buildout.cfg",
    ... """
    ... [buildout]
    ... parts = interpreter py
    ... versions = versions
    ... develop = %s
    ...
    ... [versions]
    ... zc.recipe.egg = 1.0.0
    ... setuptools = 0.6c11
    ... zc.recipe.testrunner = 1.0.0
    ... zc.buildout = 1.0.0
    ... zope.testing = 3.5.0
    ...
    ... [interpreter]
    ... recipe = zc.recipe.egg
    ... eggs = zc.recipe.wrapper
    ... interpreter = basepy
    ...
    ... [py-environment]
    ... LD_LIBRARY = some_library_I_like
    ...
    ... [py]
    ... recipe = zc.recipe.wrapper
    ... target = bin/${interpreter:interpreter}
    ... environment = py-environment
    ... """ % wrapper)
    >>> os.chdir(sample_buildout)
    >>> buildout.install([])
    Develop: '...'
    Installing interpreter.
    Getting distribution for 'zope.testing==3.5.0'.
    Got zope.testing 3.5.0.
    Getting distribution for 'zc.recipe.testrunner==1.0.0'.
    Got zc.recipe.testrunner 1.0.0.
    Getting distribution for 'zc.recipe.egg==1.0.0'.
    Got zc.recipe.egg 1.0.0.
    Generated interpreter 'PREFIX/bin/basepy'.
    Installing py.

    >>> buildout_pprint(dict(buildout))
    {'buildout': {...},
     'interpreter': {...
                     'interpreter': 'basepy',
                     'recipe': 'zc.recipe.egg'},
     'py': {'deployment': '',
            'environment': 'py-environment',
            'if-os': 'ANY',
            'name': 'py',
            'path': 'PREFIX/bin/py',
            'recipe': 'zc.recipe.wrapper',
            'target': 'bin/basepy'},
     'py-environment': {'LD_LIBRARY': 'some_library_I_like'},
     'versions': {...}}
    >>> print ls(os.path.join(sample_buildout, 'bin/py'))
    -rwxr-xr-x USER GROUP PREFIX/bin/py
    >>> print ls(os.path.join(sample_buildout, 'bin/basepy'))
    -rwxr-xr-x USER GROUP PREFIX/bin/basepy
    >>> cat(sample_buildout, 'bin', 'py')
    #!...
    import os
    import sys
    env = {}
    env.update(os.environ)
    newenv = {'LD_LIBRARY': 'some_library_I_like'}
    env.update(newenv)
    target = 'bin/basepy'
    base = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
    base = os.path.dirname(base)
    path = os.path.join(
        *([os.sep,] + base.split(os.sep) + target.split(os.sep)))
    args = [sys.executable] + [path] + sys.argv[1:]
    os.execve(sys.executable, args, env)
    >>> os.chdir(wrapper)

This bin/py will replace itself with a call to bin/basepy, baking in the added
environment.  More environment could be added by putting more options in the
`py` section.


Platform Specific Wrappers
--------------------------

Environment variables are often platform specific.  It is possible to use the
`if-os` option to confine building of a wrapper to a particular platform.

The following buildout is Linux specific.  We'll mokeypatch the function that
gets the platform to ensure that this test runs on all platforms.

    >>> import zc.recipe.wrapper
    >>> zc.recipe.wrapper.get_platform = lambda: 'linux2'
    >>> buildout_cfg = """
    ... [buildout]
    ... parts = interpreter py
    ... versions = versions
    ... develop = %s
    ...
    ... [versions]
    ... zc.recipe.egg = 1.0.0
    ... setuptools = 0.6c11
    ... zc.recipe.testrunner = 1.0.0
    ... zc.buildout = 1.0.0
    ... zope.testing = 3.5.0
    ...
    ... [interpreter]
    ... recipe = zc.recipe.egg
    ... eggs = zc.recipe.wrapper
    ... interpreter = basepy
    ...
    ... [py-environment]
    ... LD_LIBRARY = some_library_I_like
    ...
    ... [py]
    ... recipe = zc.recipe.wrapper
    ... if-os = linux2
    ... target = bin/${interpreter:interpreter}
    ... environment = py-environment
    ... """ % wrapper
    >>> buildout = setupBuildout(sample_buildout, "buildout.cfg", buildout_cfg)
    >>> os.chdir(sample_buildout)
    >>> buildout.install([])
    Develop: '...'
    Installing interpreter.
    Getting distribution for 'zope.testing==3.5.0'.
    Got zope.testing 3.5.0.
    Getting distribution for 'zc.recipe.testrunner==1.0.0'.
    Got zc.recipe.testrunner 1.0.0.
    Getting distribution for 'zc.recipe.egg==1.0.0'.
    Got zc.recipe.egg 1.0.0.
    Generated interpreter 'PREFIX/bin/basepy'.
    Installing py.
    >>> print ls(os.path.join(sample_buildout, 'bin/py'))
    -rwxr-xr-x USER GROUP PREFIX/bin/py
    >>> os.chdir(wrapper)

Now, suppose we were to run it on a Macintosh?

    >>> zc.recipe.wrapper.get_platform = lambda: 'darwin'
    >>> buildout = setupBuildout(sample_buildout, "buildout.cfg", buildout_cfg)
    >>> os.chdir(sample_buildout)
    >>> buildout.install([])
    Develop: '...'
    Installing interpreter.
    Getting distribution for 'zope.testing==3.5.0'.
    Got zope.testing 3.5.0.
    Getting distribution for 'zc.recipe.testrunner==1.0.0'.
    Got zc.recipe.testrunner 1.0.0.
    Getting distribution for 'zc.recipe.egg==1.0.0'.
    Got zc.recipe.egg 1.0.0.
    Generated interpreter 'PREFIX/bin/basepy'.
    Installing py.
    Unused options for py: 'environment' 'target'.
    >>> print ls(os.path.join(sample_buildout, 'bin/py'))
    Traceback (most recent call last):
        ...
    OSError: [Errno 2] No such file or directory: '/.../sample-buildout/bin/py'

Note that the `bin/py` script was not installed.


Required Options
----------------

zc.recipe.wrapper requires this option:

target
    The relative path of the program to execute respective to the deployment or
    the ${buildout:directory}.
environment
    The name of a section which will be used to construct the environment
    mapping.


Optional Options
----------------

There are some optional options that can be provided to zc.recipe.wrapper to
modify its function:

deployment
    The name of the zc.recipe.deployment part that sets where to put the
    wrapper, where it should look for its target, and the user who will have
    permissions.  If this is not provided, ${buildout:directory} will be used for
    the directory, and the permissions will be those of the user who runs the
    buildout.
if-os
    This can be filled in with a string, or space delimited sequence of
    strings, which are the set of values sys.platform must return in order for
    this recipe to be installed.  Defaults to 'ANY', meaning that the part is
    OS-agnostic.
name
    This is the name of the script to create.  Defaults to the name of the
    part.
