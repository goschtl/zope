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
macro recipe, and identifies the "macro section" using the "macro" option:

    >>> buildout = setupBuildout(sample_buildout, "buildout.cfg",
    ... """
    ... [buildout]
    ... parts = instance0 instance1
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
    >>> os.chdir(sample_buildout)
    >>> buildout.install([])
    >>> buildout_pprint(dict(buildout))
    {'buildout': ...
     'instance-macro': {'application': 'application',
                        'zope.conf': '
            <eventlog>
            <logfile>
            path /var/log/myapp/$${:__name__}-z3.log
            </logfile>
            </eventlog>
            <product-config zc.z3monitor>
            port $${:monitor-port}
            </product-config>'},
     'instance0': {'address': '8080',
                   'application': 'application',
                   'monitor-port': '8089',
                   'recipe': 'zc.recipe.macro:test',
                   'result-sections': 'instance0',
                   'zope.conf': '
            <eventlog>
            <logfile>
            path /var/log/myapp/instance0-z3.log
            </logfile>
            </eventlog>
            <product-config zc.z3monitor>
            port 8089
            </product-config>'},
     'instance1': {'address': '9080',
                   'application': 'application',
                   'monitor-port': '9089',
                   'recipe': 'zc.recipe.macro:test',
                   'result-sections': 'instance1',
                   'zope.conf': '
            <eventlog>
            <logfile>
            path /var/log/myapp/instance1-z3.log
            </logfile>
            </eventlog>
            <product-config zc.z3monitor>
            port 9089
            </product-config>'}}
    >>> os.chdir(macro)


This results in parts equivalent to the buildout:

    >>> os.chdir(here)
    >>> rmdir(sample_buildout)
    >>> sample_buildout = tmpdir(sample_buildout)
    >>> write(sample_buildout, "buildout.cfg",
    ... """
    ... [buildout]
    ... parts = instance0 instance1
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
    >>> buildout.install([])
    >>> buildout_pprint(dict(buildout))
    {'buildout': {...},
     'instance-macro': {'application': 'application',
                        'zope.conf': '
            <eventlog>
            <logfile>
            path /var/log/myapp/$${:__name__}-z3.log
            </logfile>
            </eventlog>
            <product-config zc.z3monitor>
            port $${:monitor-port}
            </product-config>'},
     'instance0': {'address': '8080',
                   'application': 'application',
                   'monitor-port': '8089',
                   'recipe': 'zc.recipe.macro:test',
                   'result-sections': 'instance0',
                   'zope.conf': '
            <eventlog>
            <logfile>
            path /var/log/myapp/instance0-z3.log
            </logfile>
            </eventlog>
            <product-config zc.z3monitor>
            port 8089
            </product-config>'},
     'instance1': {'address': '9080',
                   'application': 'application',
                   'monitor-port': '9089',
                   'recipe': 'zc.recipe.macro:test',
                   'result-sections': 'instance1',
                   'zope.conf': '
            <eventlog>
            <logfile>
            path /var/log/myapp/instance1-z3.log
            </logfile>
            </eventlog>
            <product-config zc.z3monitor>
            port 9089
            </product-config>'}}
    >>> os.chdir(macro)

Note that the options from the invocation are used both to perform
substitutions and as additional options in the expansion.  The result-recipe
option is used to determine the recipe used on the resulting part.

Macro invocation without a result-recipe
----------------------------------------

Sometimes it is good to have a macro that does not result in a part.

    >>> buildout = setupBuildout(sample_buildout, "buildout.cfg",
    ... """
    ... [buildout]
    ... parts = instance0 instance1
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
    >>> buildout.install([])
    >>> buildout_pprint(buildout)
    {'buildout': {...},
     'instance-macro': {'application': 'application',
                        'zope.conf': '
            <eventlog>
            <logfile>
            path /var/log/myapp/$${:__name__}-z3.log
            </logfile>
            </eventlog>
            <product-config zc.z3monitor>
            port $${:monitor-port}
            </product-config>'},
     'instance0': {'address': '8080',
                   'application': 'application',
                   'monitor-port': '8089',
                   'recipe': 'zc.recipe.macro:empty',
                   'result-sections': 'instance0',
                   'zope.conf': '
            <eventlog>
            <logfile>
            path /var/log/myapp/instance0-z3.log
            </logfile>
            </eventlog>
            <product-config zc.z3monitor>
            port 8089
            </product-config>'},
     'instance1': {'address': '9080',
                   'application': 'application',
                   'monitor-port': '9089',
                   'recipe': 'zc.recipe.macro:empty',
                   'result-sections': 'instance1',
                   'zope.conf': '
            <eventlog>
            <logfile>
            path /var/log/myapp/instance1-z3.log
            </logfile>
            </eventlog>
            <product-config zc.z3monitor>
            port 9089
            </product-config>'}}
    >>> os.chdir(sample_buildout)

In this case, the zc.recipe.macro recipe is used, with its Empty entry point.
This entry point doesn't do anything, but we have to have a recipe to use,
since the macro recipe has declared this to be a part.  The same sort of output
will come from an empty result-recipe option.

    >>> buildout = setupBuildout(sample_buildout, "buildout.cfg",
    ... """
    ... [buildout]
    ... parts = instance0 instance1
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
    >>> buildout.install([])
    >>> buildout_pprint(buildout)
    {'buildout': {...},
     'instance-macro': {'application': 'application',
                        'zope.conf': '
            <eventlog>
            <logfile>
            path /var/log/myapp/$${:__name__}-z3.log
            </logfile>
            </eventlog>
            <product-config zc.z3monitor>
            port $${:monitor-port}
            </product-config>'},
     'instance0': {'address': '8080',
                   'application': 'application',
                   'monitor-port': '8089',
                   'recipe': 'zc.recipe.macro:empty',
                   'result-sections': 'instance0',
                   'zope.conf': '
            <eventlog>
            <logfile>
            path /var/log/myapp/instance0-z3.log
            </logfile>
            </eventlog>
            <product-config zc.z3monitor>
            port 8089
            </product-config>'},
     'instance1': {'address': '9080',
                   'application': 'application',
                   'monitor-port': '9089',
                   'recipe': 'zc.recipe.macro:empty',
                   'result-sections': 'instance1',
                   'zope.conf': '
            <eventlog>
            <logfile>
            path /var/log/myapp/instance1-z3.log
            </logfile>
            </eventlog>
            <product-config zc.z3monitor>
            port 9089
            </product-config>'}}

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

    >>> buildout = setupBuildout(sample_buildout, "buildout.cfg",
    ... """
    ... [buildout]
    ... parts = invoker
    ...
    ... [macro]
    ... output = I was invoked on $${:__name__}
    ...
    ... [invoker]
    ... recipe = zc.recipe.macro
    ... macro = macro
    ... targets =
    ...     zero
    ...     one
    ... """)
    >>> buildout.install([])
    >>> buildout_pprint(buildout)
    {'buildout': {...},
     'invoker': {'recipe': 'zc.recipe.macro:empty', 'result-sections': 'zero one'},
     'macro': {'output': 'I was invoked on $${:__name__}'},
     'one': {'output': 'I was invoked on one'},
     'zero': {'output': 'I was invoked on zero'}}

It is possible, and much more useful, to provide parameters by specifying other
sections.

    >>> buildout = setupBuildout(sample_buildout, "buildout.cfg",
    ... """
    ... [buildout]
    ... parts = invoker
    ...
    ... [macro]
    ... output = $${:subject} was invoked on $${:__name__}
    ...
    ... [one-parameters]
    ... subject = Fred
    ...
    ... [zero-parameters]
    ... subject = Benji
    ...
    ... [invoker]
    ... recipe = zc.recipe.macro
    ... macro = macro
    ... targets =
    ...     zero:zero-parameters
    ...     one:one-parameters
    ... """)
    >>> buildout.install([])
    >>> buildout_pprint(buildout)
    {'buildout': {...},
     'invoker': {'recipe': 'zc.recipe.macro:empty', 'result-sections': 'zero one'},
     'macro': {'output': '$${:subject} was invoked on $${:__name__}'},
     'one': {'output': 'Fred was invoked on one'},
     'one-parameters': {'subject': 'Fred'},
     'zero': {'output': 'Benji was invoked on zero'},
     'zero-parameters': {'subject': 'Benji'}}


Default values in macros
------------------------

It is possible to make default values in macros.

    >>> buildout = setupBuildout(sample_buildout, "buildout.cfg",
    ... """
    ... [buildout]
    ... parts = instance0
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
    ... address = 8080
    ... monitor-port = 8089
    ...
    ... [instance0]
    ... recipe = zc.recipe.macro
    ... result-recipe = zc.recipe.macro:test
    ... macro = instance-macro
    ... """)
    >>> os.chdir(sample_buildout)
    >>> buildout.install([])
    >>> buildout_pprint(dict(buildout))
    {'buildout': {...},
     'instance-macro': {'address': '8080',
                        'application': 'application',
                        'monitor-port': '8089',
                        'zope.conf': '
            <eventlog>
            <logfile>
            path /var/log/myapp/$${:__name__}-z3.log
            </logfile>
            </eventlog>
            <product-config zc.z3monitor>
            port $${:monitor-port}
            </product-config>'},
     'instance0': {'address': '8080',
                   'application': 'application',
                   'monitor-port': '8089',
                   'recipe': 'zc.recipe.macro:test',
                   'result-sections': 'instance0',
                   'zope.conf': '
            <eventlog>
            <logfile>
            path /var/log/myapp/instance0-z3.log
            </logfile>
            </eventlog>
            <product-config zc.z3monitor>
            port 8089
            </product-config>'}}
    >>> os.chdir(macro)

    >>> buildout = setupBuildout(sample_buildout, "buildout.cfg",
    ... """
    ... [buildout]
    ... parts = invoker
    ...
    ... [macro]
    ... output = $${:subject} $${:verb} on $${:__name__}
    ... subject = I
    ... verb = was invoked
    ...
    ... [zero-parameters]
    ... verb = drive
    ...
    ... [invoker]
    ... recipe = zc.recipe.macro
    ... macro = macro
    ... targets = zero:zero-parameters
    ... """)
    >>> buildout.install([])
    >>> buildout_pprint(buildout)
    {'buildout': {...},
     'invoker': {'recipe': 'zc.recipe.macro:empty', 'result-sections': 'zero'},
     'macro': {'output': '$${:subject} $${:verb} on $${:__name__}',
               'subject': 'I',
               'verb': 'was invoked'},
     'zero': {'output': 'I drive on zero', 'verb': 'drive', 'subject': 'I'},
     'zero-parameters': {'verb': 'drive'}}


Edge Case Tests
---------------

It used to cause errors when default macro variables referred to one another
and the invoker targetted itself.  This test will prevent regression.  The bug
is dependant on the iteration order of a dictionaryish object, and so a
subclass will be created that returns it's keys in a particular order.

    >>> import zc.recipe.macro.recipe
    >>> class OrderedOptions(zc.buildout.buildout.Options):
    ...     def keys(self):
    ...         return list(
    ...             reversed(sorted(zc.buildout.buildout.Options.keys(self))))
    >>> zc.recipe.macro.recipe.Options = OrderedOptions

Now we'll make the buildout in memory, so that our monkeypatch will be effective:

    >>> buildout = setupBuildout(sample_buildout, "buildout.cfg",
    ... """
    ... [buildout]
    ... parts = instance0
    ...
    ... [instance-macro]
    ... address = 8080
    ... application = application
    ... monitor-port = 8089
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
    ... """)
    >>> buildout.install([])
    >>> buildout_pprint(buildout)
    {'buildout': {...},
     'instance-macro': {'address': '8080',
                        'application': 'application',
                        'monitor-port': '8089',
                        'zope.conf': '
            <eventlog>
            <logfile>
            path /var/log/myapp/$${:__name__}-z3.log
            </logfile>
            </eventlog>
            <product-config zc.z3monitor>
            port $${:monitor-port}
            </product-config>'},
     'instance0': {'address': '8080',
                   'application': 'application',
                   'monitor-port': '8089',
                   'recipe': 'zc.recipe.macro:test',
                   'result-sections': 'instance0',
                   'zope.conf': '
            <eventlog>
            <logfile>
            path /var/log/myapp/instance0-z3.log
            </logfile>
            </eventlog>
            <product-config zc.z3monitor>
            port 8089
            </product-config>'}}

And we'll return to the old Options:

    >>> zc.recipe.macro.recipe.Options = zc.buildout.buildout.Options

