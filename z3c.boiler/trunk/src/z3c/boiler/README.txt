======================================
ZBoiler - A Quick Way to Boil Projects
======================================

The ZBoiler package provides a small script to generate the boilerplate of a
project from a simple, high-level feature XML file. An example of such a
configuration file is `sample-project.xml`.

  >>> from z3c.boiler import script

  >>> def boil(args, showLog=False):
  ...     try:
  ...         script.main(args)
  ...     except SystemExit, err:
  ...         print 'Exit Code: %i' % err.code
  ...     else:
  ...         print 'Error: No proper exit.'

Let's generate the project using the script. We need to specify the
configuration file and a target directory.

    >>> import os
    >>> featureFile = os.path.join(
    ...     os.path.dirname(script.__file__), 'sample-project.xml')

    >>> boil(['-i', featureFile, '-o', buildPath])
    INFO - Creating directory .../z3c.sampleproject
    INFO - Creating file .../z3c.sampleproject/bootstrap.py
    INFO - Creating file .../z3c.sampleproject/setup.py
    INFO - Creating file .../z3c.sampleproject/buildout.cfg
    INFO - Creating directory .../z3c.sampleproject/src
    INFO - Creating directory .../z3c.sampleproject/src/z3c
    INFO - Creating directory .../z3c.sampleproject/src/z3c/sampleproject
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/application.zcml
    INFO - Creating directory .../z3c.sampleproject/src/z3c/sampleproject/browser
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/browser/configure.zcml
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/browser/message.py
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/browser/__init__.py
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/configure.zcml
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/interfaces.py
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/index.txt
    INFO - Creating directory .../z3c.sampleproject/src/z3c/sampleproject/tests
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/tests/test_doc.py
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/tests/__init__.py
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/README.txt
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/message.py
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/__init__.py
    INFO - Creating file .../z3c.sampleproject/src/z3c/__init__.py
    INFO - Creating file .../z3c.sampleproject/ZBOILER.txt
    INFO - Build finished
    Exit Code: 0

Let's now have a look at the generated directory:

    >>> ls(buildPath)
    z3c.sampleproject/
      ZBOILER.txt
      bootstrap.py
      buildout.cfg
      setup.py
      src/
        z3c/
          __init__.py
          sampleproject/
            README.txt
            __init__.py
            application.zcml
            configure.zcml
            index.txt
            interfaces.py
            message.py
            browser/
              __init__.py
              configure.zcml
              message.pytests/
              __init__.py
              test_doc.py

When we try to regenerate the project again, we get a failure, since the
directory already exists:

  >>> boil(['-i', featureFile, '-o', buildPath])
  CRITICAL - Failed building package because file .../z3c.sampleproject
             already exists.  Use --force to overwrite it.
  Exit Code: 1

We can, however, force the directory to be overwritten as the message
mentions:

    >>> boil(['-f', '-i', featureFile, '-o', buildPath])
    INFO - Creating directory .../z3c.sampleproject
    INFO - Creating file .../z3c.sampleproject/bootstrap.py
    INFO - Creating file .../z3c.sampleproject/setup.py
    INFO - Creating file .../z3c.sampleproject/buildout.cfg
    INFO - Creating directory .../z3c.sampleproject/src
    INFO - Creating directory .../z3c.sampleproject/src/z3c
    INFO - Creating directory .../z3c.sampleproject/src/z3c/sampleproject
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/application.zcml
    INFO - Creating directory .../z3c.sampleproject/src/z3c/sampleproject/browser
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/browser/configure.zcml
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/browser/message.py
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/browser/__init__.py
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/configure.zcml
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/interfaces.py
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/index.txt
    INFO - Creating directory .../z3c.sampleproject/src/z3c/sampleproject/tests
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/tests/test_doc.py
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/tests/__init__.py
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/README.txt
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/message.py
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/__init__.py
    INFO - Creating file .../z3c.sampleproject/src/z3c/__init__.py
    INFO - Creating file .../z3c.sampleproject/ZBOILER.txt
    INFO - Build finished
    Exit Code: 0

If we want less information, we can simply tell the script to be quiet:

  >>> boil(['-q', '-f', '-i', featureFile, '-o', buildPath])
  Exit Code: 0

Fatal messages are still displayed:

  >>> boil(['-q', '-i', featureFile, '-o', buildPath])
  CRITICAL - Failed building package because file .../z3c.sampleproject
             already exists.  Use --force to overwrite it.
  Exit Code: 1

We can also ask for more information:

    >>> boil(['-v', '-f', '-i', featureFile, '-o', buildPath])
    DEBUG - Updating <SimpleFileBuilder u'bootstrap.py'>
    DEBUG - Updating <PartBuilder u'versions'>
    DEBUG - Updating <PartBuilder u'zope3'>
    DEBUG - Updating <PartBuilder u'z3c.sampleproject-app'>
    DEBUG - Updating <PartBuilder u'z3c.sampleproject'>
    DEBUG - Updating <PartBuilder u'database'>
    DEBUG - Updating <PartBuilder u'docs'>
    DEBUG - Updating <PartBuilder u'python'>
    DEBUG - Updating <PartBuilder u'test'>
    DEBUG - Updating <PartBuilder u'coverage-test'>
    DEBUG - Updating <PartBuilder u'coverage-report'>
    DEBUG - Updating <PackageBuilder u'z3c'>
    DEBUG - Updating <PackageBuilder u'sampleproject'>
    DEBUG - Updating <PackageBuilder u'browser'>
    DEBUG - Updating <ModuleBuilder u'message.py'>
    DEBUG - Updating <ModuleBuilder u'interfaces.py'>
    DEBUG - Updating <PackageBuilder u'tests'>
    DEBUG - Updating <SimpleFileBuilder u'test_doc.py'>
    DEBUG - Updating <SimpleFileBuilder u'README.txt'>
    DEBUG - Updating <ModuleBuilder u'message.py'>
    DEBUG - Updating <FeatureDocBuilder u'ZBOILER.txt'>
    INFO - Creating directory .../z3c.sampleproject
    INFO - Creating file .../z3c.sampleproject/bootstrap.py
    INFO - Creating file .../z3c.sampleproject/setup.py
    INFO - Creating file .../z3c.sampleproject/buildout.cfg
    INFO - Creating directory .../z3c.sampleproject/src
    INFO - Creating directory .../z3c.sampleproject/src/z3c
    INFO - Creating directory .../z3c.sampleproject/src/z3c/sampleproject
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/application.zcml
    INFO - Creating directory .../z3c.sampleproject/src/z3c/sampleproject/browser
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/browser/configure.zcml
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/browser/message.py
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/browser/__init__.py
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/configure.zcml
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/interfaces.py
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/index.txt
    INFO - Creating directory .../z3c.sampleproject/src/z3c/sampleproject/tests
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/tests/test_doc.py
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/tests/__init__.py
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/README.txt
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/message.py
    INFO - Creating file .../z3c.sampleproject/src/z3c/sampleproject/__init__.py
    INFO - Creating file .../z3c.sampleproject/src/z3c/__init__.py
    INFO - Creating file .../z3c.sampleproject/ZBOILER.txt
    INFO - Build finished
    Exit Code: 0

It is also possible to use a built in project template as a basis for
a new project.  To see an available list of built in templates, we use
the --list option.

  >>> boil(['--list'])
  Available Templates:
  <BLANKLINE>
    zope-project   "Zope 3 Web Application"
                     Includes all the features you would want for a Zope 3 Web Application.
    command-line   "Command Line Program"
                     Includes all the features you would want for a command line program.
    python-package "Python Package"
                     Just a simple python package with few bells and whistles.
  Exit Code: 0

If we try to use a template that does not exist, then we are told to
use --list:

  >>> boil(['-t','foobar'])
  Could not find the template "foobar".
  Use --list to see available templates.
  Exit Code: 1


Last but not least, we also have some help for the `boil` script:

  >>> boil(['-h'])
  Usage: test [options]
  <BLANKLINE>
  Options:
    -h, --help            show this help message and exit
    -i FILE, --input-file=FILE
                          The file containing the XML definition of the project.
    -t TEMPLATE, --template=TEMPLATE
                          A project template.  Use --list to see available
                          templates
    -l, --list            Show a list of available templates for use with
                          --template
    -k, --interactive     When specified, runs in interactive mode prompting you
                          to enter missing values.
    -o DIR, --output-dir=DIR
                          The directory where project files should be generated.
    -q, --quiet           When specified, no messages are displayed.
    -v, --verbose         When specified, debug information is created.
    -f, --force           Force the package to be generated even overwriting any
                          existing files.
  Exit Code: 0

When no arguments are specified, help is also shown:

  >>> boil([])
  Usage: test [options]
  ...
  Exit Code: 0
