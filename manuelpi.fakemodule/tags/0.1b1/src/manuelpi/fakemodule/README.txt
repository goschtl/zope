Intro and Motivation
====================

`manuelpi.fakemodule` is a plugin for `Manuel`_ that supports syntax 
for creating modules within a doctest. The module, once defined, is then
usable by subsequent doctest statements.

This functionality is useful for packages that you might describe as
being 'meta'; they operate on modules. Thus, being able to define
and then process modules within the same doctest using a clean and 
uncluttered syntax is extremely beneficial. 

One such package to benefit from this sort of facility is `Martian`_, 
which scans modules for configuration directives, registering them as
it goes.

.. _Martian: http://pypi.python.org/pypi/martian
.. _Manuel: http://packages.python.org/manuel

Usage
=====

The special REStructure Text directive::

'.. module-block:: <MODULE_NAME>' 

is used to denote the start of a module and its alias <MODULE_NAME> for 
the rest of the doctest. We then define the module's body at a single 
indentation level after this directive. What follows is an example of a 
full doctest::

 We create a new module with a main function to perform this task::

 .. module-block:: test_module 

    import sys

    class A:
        def do_something(self):
            return "Hello World"

    def main():
        print A().do_something()

  Now let's execute the main function

.. ignore-next-block

::

    >>> test_module.main()
    Hello World

The above doctest creates a new module `test_module` and then exercises
the objects within it. Notice how the module becomes immediately available
to the doctet after its definition. 

To use `manualpi.fakemodule` in your application, set up your tests as
described in the Manuel documentation and import the `Manuel` class from
`manuelpi.fakemodule`::

  ...
  import manuelpi.fakemodule
  ...
  m += manuelpi.fakemodule.Manuel()
