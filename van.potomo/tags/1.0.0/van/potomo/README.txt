Purpose
=======

This package integrates pure-python gettext translation compilation (msgfmt)
into the setup.py "build" and "develop" commands.

These commands are extended so that every "data file" identified by setuptools
with the .po extension is compiled to a .mo file in the same directory as the
.po file.

This integrates very well if you use z3c.recipe.i18n (and hopefully others as
well) to manage .po files.

Usage
=====

You need to override the "build" and "develop" commands in your setup.py, for example::

    from setuptools import setup, find_packages
    from van.potomo import develop, build

    setup(
        name = "HelloWorld",
        cmdclass={'build': build,
                  'develop': develop},
        setup_requires=["van.potomo"],
        version = "0.1",
        packages = find_packages(),
    )

Why
===

This package exists because the author believes that:

* Compiled translations should not be stored under revision control, they are not source
* Compiled translations should not be distributed in tarballs, they are not source
* Compiled translations should not be "lazily compiled" unless you take into account that
  filesystems on production machines are often read-only.
* The process of compiling translations should not require an extra step/options during
  the build/install or build/develop cycle.

The options available at the time offered all of this:

* Babel: Not integrated into the "build" distutils command. 
* cc.gettext: Depends on buildout, not useful for deployments by other means.
* zope.i18n lazy compilation: Very nice for development, but not on some
  production environments.


Caveats
=======

van.potomo makes your setup.py depend on van.potomo. But outside tools cannot
tell this because they need to run the setup.py to figure out the dependencies.

Basically this means your developers/users will need to install van.potomo
manually before anything else. If anyone knows a robust/good way to get around
this limitation, please let the author know.
