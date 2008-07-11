==========================
Invoking recipes as macros
==========================

This recipe provides a macro system for buildout parts; the intent is to avoid
repitition in buildout configurations.  For buildouts creating several Zope 3
instances, we've commonly observed that the zope.conf option gets fairly large
and is repeated for each instance to allow a few substitutions in the middle
(port numbers and logfile paths are the main culprits).  Pushing the bulk of
the zope.conf setting to a macro to avoid repeating the syntax, and allowing
that to refer to settings that are actually specific to instance would
significantly improve both readability and maintainability of the instace
configurations.

The macro recipe allows storing the common portions of a part in a section
that's referred to as a "macro section"; it defines everything common to parts
that use it, except the recipe option.

Macros are used by parts called "macro invocations".  The invocation uses the
macro recipe, and identifies the "macro section" using the "macro" option::

    >>> write(sample_buildout, "buildout.cfg",
    ... """
    ... [buildout]
    ... parts = instance0 instance1
    ... versions = versions
    ...
    ... [versions]
    ... zc.recipe.egg = 1.0.0
    ... setuptools = 0.6c8
    ... zc.recipe.testrunner = 1.0.0
    ... zc.buildout = 1.0.0
    ... zope.testing = 3.5.0
    ...
    ... [instance-macro]
    ... application = application
    ... zope.conf =
    ...     <eventlog>
    ...         <logfile>
    ...             path /var/log/myapp/$${:__name__}-z3.log
    ...         </logfile>
    ...     </eventlog>
    ...     <product-config zc.z3monitor>
    ...         port $${:monitor-port}
    ...     </product-config>
    ...
    ... [instance0]
    ... recipe = zc.recipe.macro
    ... result-recipe = zc.recipe.macro:test
    ... macro = instance-macro
    ... address = 8080
    ... monitor-port = 8089
    ...
    ... [instance1]
    ... recipe = zc.recipe.macro
    ... result-recipe = zc.recipe.macro:test
    ... macro = instance-macro
    ... address = 9080
    ... monitor-port = 9089
    ... """)

- The ``[buildout]`` section specified two parts, ``instance0`` and
  ``instance1``.

- These parts in turn specified that they would be using the
  macro system: ``recipe = zc.recipe.macro``.

- The output of the macro should be used with the ``zc.recipe.macro:test``
  recipe, as specified by the ``result-recipe`` option.

- This resulting recipe will receive the ``address`` option from the two
  instance sections.

- It will also receive the (unprocessed) ``application`` option from the
  ``instance-macro``.

- The recipe will also receive the fully processed result of the
  ``instance-macro`` ``zope.conf`` option.

  The zope.conf has two substitutions.  They both use the prefix ``$${:``
  and the suffix ``}``.  This syntax is driven in part by the needs of the
  ConfigParser library on which zc.buildout relies.
  
  * The ``monitor-port`` is replaced with the ``monitor-port`` values from
    the ``instance0`` and ``instance1`` sections, respectively.

  * The ``__name__`` is a special token that is replaced with the name of
    the section--in this case the strings "instance0" and "instance1"
    respectively.

Now we'll run the buildout.

    >>> import os
    >>> here = os.getcwd()
    >>> os.chdir(sample_buildout)
    >>> buildout = os.path.join(sample_buildout, 'bin', 'buildout')
    >>> print system(buildout)
    Installing instance0.
        address: 8080
        application: application
        monitor-port: 8089
        recipe: zc.recipe.macro:test
        zope.conf: 
            <eventlog>
                <logfile>
                    path /var/log/myapp/instance0-z3.log
                </logfile>
            </eventlog>
            <product-config zc.z3monitor>
                port 8089
            </product-config>
    Installing instance1.
        address: 9080
        application: application
        monitor-port: 9089
        recipe: zc.recipe.macro:test
        zope.conf: 
            <eventlog>
                <logfile>
                    path /var/log/myapp/instance1-z3.log
                </logfile>
            </eventlog>
            <product-config zc.z3monitor>
                port 9089
            </product-config>
    <BLANKLINE>


This results in parts equivalent to the buildout::

    >>> os.chdir(here)
    >>> write(sample_buildout, "buildout.cfg",
    ... """
    ... [buildout]
    ... parts = instance0 instance1
    ... versions = versions
    ...
    ... [versions]
    ... zc.recipe.egg = 1.0.0
    ... setuptools = 0.6c8
    ... zc.recipe.testrunner = 1.0.0
    ... zc.buildout = 1.0.0
    ... zope.testing = 3.5.0
    ...
    ... [instance0]
    ... recipe = zc.recipe.macro:test
    ... application = application
    ... address = 8080
    ... monitor-port = 8089
    ... zope.conf =
    ...     <eventlog>
    ...         <logfile>
    ...             path /var/log/myapp/instance0-z3.log
    ...         </logfile>
    ...     </eventlog>
    ...     <product-config zc.z3monitor>
    ...         port ${instance0:monitor-port}
    ...     </product-config>
    ...
    ... [instance1]
    ... recipe = zc.recipe.macro:test
    ... application = application
    ... address = 9080
    ... monitor-port = 9089
    ... zope.conf =
    ...     <eventlog>
    ...         <logfile>
    ...             path /var/log/myapp/instance1-z3.log
    ...         </logfile>
    ...     </eventlog>
    ...     <product-config zc.z3monitor>
    ...         port ${instance1:monitor-port}
    ...     </product-config>
    ... """)
    >>> os.chdir(sample_buildout)
    >>> print system(buildout)
    Updating instance0.
        address: 8080
        application: application
        monitor-port: 8089
        recipe: zc.recipe.macro:test
        zope.conf: 
            <eventlog>
                <logfile>
                    path /var/log/myapp/instance0-z3.log
                </logfile>
            </eventlog>
            <product-config zc.z3monitor>
                port 8089
            </product-config>
    Updating instance1.
        address: 9080
        application: application
        monitor-port: 9089
        recipe: zc.recipe.macro:test
        zope.conf: 
            <eventlog>
                <logfile>
                    path /var/log/myapp/instance1-z3.log
                </logfile>
            </eventlog>
            <product-config zc.z3monitor>
                port 9089
            </product-config>
    <BLANKLINE>

Note that the options from the invocation are used both to perform
substitutions and as additional options in the expansion.  The result-recipe
option is used to determine the recipe used on the resulting part.

Macro invocation without a result-recipe
----------------------------------------

Sometimes it is good to have a macro that does not result in a part.

    >>> os.chdir(here)
    >>> write(sample_buildout, "buildout.cfg",
    ... """
    ... [buildout]
    ... parts = instance0 instance1
    ... versions = versions
    ...
    ... [versions]
    ... zc.recipe.egg = 1.0.0
    ... setuptools = 0.6c8
    ... zc.recipe.testrunner = 1.0.0
    ... zc.buildout = 1.0.0
    ... zope.testing = 3.5.0
    ...
    ... [instance-macro]
    ... application = application
    ... zope.conf =
    ...     <eventlog>
    ...         <logfile>
    ...             path /var/log/myapp/$${:__name__}-z3.log
    ...         </logfile>
    ...     </eventlog>
    ...     <product-config zc.z3monitor>
    ...         port $${:monitor-port}
    ...     </product-config>
    ...
    ... [instance0]
    ... recipe = zc.recipe.macro
    ... macro = instance-macro
    ... address = 8080
    ... monitor-port = 8089
    ...
    ... [instance1]
    ... recipe = zc.recipe.macro
    ... macro = instance-macro
    ... address = 9080
    ... monitor-port = 9089
    ... """)

    >>> os.chdir(sample_buildout)
    >>> buildout = os.path.join(sample_buildout, 'bin', 'buildout')
    >>> print system(buildout + ' -vv')
    Installing 'zc.buildout', 'setuptools'.
    ...
    <BLANKLINE>
    Configuration data:
    [instance-macro]
    application = application
    zope.conf = %(__buildout_space_n__)s<eventlog>
        <logfile>
        path /var/log/myapp/$${:__name__}-z3.log
        </logfile>
        </eventlog>
        <product-config zc.z3monitor>
        port $${:monitor-port}
        </product-config>
    [instance0]
    address = 8080
    application = application
    monitor-port = 8089
    recipe = zc.recipe.macro:empty
    zope.conf = %(__buildout_space_n__)s<eventlog>
        <logfile>
        path /var/log/myapp/instance0-z3.log
        </logfile>
        </eventlog>
        <product-config zc.z3monitor>
        port 8089
        </product-config>
    [instance1]
    address = 9080
    application = application
    monitor-port = 9089
    recipe = zc.recipe.macro:empty
    zope.conf = %(__buildout_space_n__)s<eventlog>
        <logfile>
        path /var/log/myapp/instance1-z3.log
        </logfile>
        </eventlog>
        <product-config zc.z3monitor>
        port 9089
        </product-config>
    [buildout]
    bin-directory = /sample-buildout/bin
    develop-eggs-directory = /sample-buildout/develop-eggs
    directory = /sample-buildout
    eggs-directory = /sample-buildout/eggs
    executable = .../local/bin/python...
    installed = /sample-buildout/.installed.cfg
    log-format =
    log-level = INFO
    newest = true
    offline = false
    parts = instance0 instance1
    parts-directory = /sample-buildout/parts
    python = buildout
    verbosity = 20
    versions = versions
    [versions]
    setuptools = 0.6c8
    zc.buildout = 1.0.0
    zc.recipe.egg = 1.0.0
    zc.recipe.testrunner = 1.0.0
    zope.testing = 3.5.0
    <BLANKLINE>
    ...

In this case, the zc.recipe.macro recipe is used, with its Empty entry point.
This entry point doesn't do anything, but we have to have a recipe to use,
since the macro recipe has declared this to be a part.  The same sort of output
will come from an empty result-recipe option.

    >>> os.chdir(here)
    >>> write(sample_buildout, "buildout.cfg",
    ... """
    ... [buildout]
    ... parts = instance0 instance1
    ... versions = versions
    ...
    ... [versions]
    ... zc.recipe.egg = 1.0.0
    ... setuptools = 0.6c8
    ... zc.recipe.testrunner = 1.0.0
    ... zc.buildout = 1.0.0
    ... zope.testing = 3.5.0
    ...
    ... [instance-macro]
    ... application = application
    ... zope.conf =
    ...     <eventlog>
    ...         <logfile>
    ...             path /var/log/myapp/$${:__name__}-z3.log
    ...         </logfile>
    ...     </eventlog>
    ...     <product-config zc.z3monitor>
    ...         port $${:monitor-port}
    ...     </product-config>
    ...
    ... [instance0]
    ... recipe = zc.recipe.macro
    ... result-recipe =
    ... macro = instance-macro
    ... address = 8080
    ... monitor-port = 8089
    ...
    ... [instance1]
    ... recipe = zc.recipe.macro
    ... result-recipe =
    ... macro = instance-macro
    ... address = 9080
    ... monitor-port = 9089
    ... """)

    >>> os.chdir(sample_buildout)
    >>> buildout = os.path.join(sample_buildout, 'bin', 'buildout')
    >>> print system(buildout + ' -vv')
    Installing 'zc.buildout', 'setuptools'.
    ...
    <BLANKLINE>
    Configuration data:
    [instance-macro]
    application = application
    zope.conf = %(__buildout_space_n__)s<eventlog>
        <logfile>
        path /var/log/myapp/$${:__name__}-z3.log
        </logfile>
        </eventlog>
        <product-config zc.z3monitor>
        port $${:monitor-port}
        </product-config>
    [instance0]
    address = 8080
    application = application
    monitor-port = 8089
    recipe = zc.recipe.macro:empty
    zope.conf = %(__buildout_space_n__)s<eventlog>
        <logfile>
        path /var/log/myapp/instance0-z3.log
        </logfile>
        </eventlog>
        <product-config zc.z3monitor>
        port 8089
        </product-config>
    [instance1]
    address = 9080
    application = application
    monitor-port = 9089
    recipe = zc.recipe.macro:empty
    zope.conf = %(__buildout_space_n__)s<eventlog>
        <logfile>
        path /var/log/myapp/instance1-z3.log
        </logfile>
        </eventlog>
        <product-config zc.z3monitor>
        port 9089
        </product-config>
    [buildout]
    bin-directory = /sample-buildout/bin
    develop-eggs-directory = /sample-buildout/develop-eggs
    directory = /sample-buildout
    eggs-directory = /sample-buildout/eggs
    executable = .../local/bin/python...
    installed = /sample-buildout/.installed.cfg
    log-format =
    log-level = INFO
    newest = true
    offline = false
    parts = instance0 instance1
    parts-directory = /sample-buildout/parts
    python = buildout
    verbosity = 20
    versions = versions
    [versions]
    setuptools = 0.6c8
    zc.buildout = 1.0.0
    zc.recipe.egg = 1.0.0
    zc.recipe.testrunner = 1.0.0
    zope.testing = 3.5.0
    <BLANKLINE>
    ...

And of course they are the same as explicitly declaring and empty result.

Targets for Macro Invocation
----------------------------

Macros don't provide for a seperate scope, by default.  This is often perfectly
fine, but if we want to make it possible to invoke the same recipe twice, there
must be a way to target the macro invocation.  The way targetting works is it
iterates over the names in the targets value, creating a section by that name
if necesary, and putting the results of the invocation in the new section.  New
sections are just like any other section, so other sections can refer to their
options, and they can be used as parts.

    >>> os.chdir(here)
    >>> write(sample_buildout, "buildout.cfg",
    ... """
    ... [buildout]
    ... parts = invoker0 invoker1
    ... versions = versions
    ...
    ... [versions]
    ... zc.recipe.egg = 1.0.0
    ... setuptools = 0.6c8
    ... zc.recipe.testrunner = 1.0.0
    ... zc.buildout = 1.0.0
    ... zope.testing = 3.5.0
    ...
    ... [macro]
    ... output = I was invoked by $${:__name__}
    ...
    ... [invoker0]
    ... recipe = zc.recipe.macro
    ... macro = macro
    ... targets = zero
    ...
    ... [invoker1]
    ... recipe = zc.recipe.macro
    ... macro = macro
    ... targets = one
    ... """)

    >>> os.chdir(sample_buildout)
    >>> buildout = os.path.join(sample_buildout, 'bin', 'buildout')
    >>> print system(buildout + ' -vv')
    Installing 'zc.buildout', 'setuptools'.
    ...
    <BLANKLINE>
    Configuration data:
    [buildout]
    bin-directory = /sample-buildout/bin
    develop-eggs-directory = /sample-buildout/develop-eggs
    directory = /sample-buildout
    eggs-directory = /sample-buildout/eggs
    executable = .../local/bin/python...
    installed = /sample-buildout/.installed.cfg
    log-format =
    log-level = INFO
    newest = true
    offline = false
    parts = invoker0 invoker1
    parts-directory = /sample-buildout/parts
    python = buildout
    verbosity = 20
    versions = versions
    [versions]
    setuptools = 0.6c8
    zc.buildout = 1.0.0
    zc.recipe.egg = 1.0.0
    zc.recipe.testrunner = 1.0.0
    zope.testing = 3.5.0
    [macro]
    output = I was invoked by $${:__name__}
    [invoker0]
    recipe = zc.recipe.macro:empty
    [invoker1]
    recipe = zc.recipe.macro:empty
    [zero]
    output = I was invoked by zero
    [one]
    output = I was invoked by one
    <BLANKLINE>
    ...


Providing Parameters to Named Macros
------------------------------------

Another thing that is necesary to being able to use a macro twice in the same
section is the ability to specify a mapping between the options of the invoker
and the options in the scope.  Without this, no matter how many times one ran
the macro, the results would all be the same.  This is done by naming an
existing section, which will be used as source of values.

    >>> os.chdir(here)
    >>> write(sample_buildout, "buildout.cfg",
    ... """
    ... [buildout]
    ... parts = invoker0
    ... versions = versions
    ...
    ... [versions]
    ... zc.recipe.egg = 1.0.0
    ... setuptools = 0.6c8
    ... zc.recipe.testrunner = 1.0.0
    ... zc.buildout = 1.0.0
    ... zope.testing = 3.5.0
    ...
    ... [macro]
    ... output = I was invoked by $${:name}
    ... name = $${:__name__}
    ...
    ... [invoker0]
    ... recipe = zc.recipe.macro
    ... result-recipe =
    ... macro = macro
    ... targets = zero:zero-parameters
    ...
    ... [zero-parameters]
    ... name = Otto von Bismark
    ... """)

    >>> os.chdir(sample_buildout)
    >>> buildout = os.path.join(sample_buildout, 'bin', 'buildout')
    >>> print system(buildout + ' -vv')
    Installing 'zc.buildout', 'setuptools'.
    ...
    <BLANKLINE>
    Configuration data:
    [zero-parameters]
    name = Otto von Bismark
    [versions]
    setuptools = 0.6c8
    zc.buildout = 1.0.0
    zc.recipe.egg = 1.0.0
    zc.recipe.testrunner = 1.0.0
    zope.testing = 3.5.0
    [macro]
    name = $${:__name__}
    output = I was invoked by $${:name}
    [invoker0]
    recipe = zc.recipe.macro:empty
    [zero]
    name = Otto von Bismark
    output = I was invoked by Otto von Bismark
    [buildout]
    bin-directory = /sample-buildout/bin
    develop-eggs-directory = /sample-buildout/develop-eggs
    directory = /sample-buildout
    eggs-directory = /sample-buildout/eggs
    executable = .../local/bin/python...
    installed = /sample-buildout/.installed.cfg
    log-format =
    log-level = INFO
    newest = true
    offline = false
    parts = invoker0
    parts-directory = /sample-buildout/parts
    python = buildout
    verbosity = 20
    versions = versions
    <BLANKLINE>
    ...


