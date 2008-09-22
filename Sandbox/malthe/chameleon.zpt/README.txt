Overview
========

This package provides a fast Zope Page Template implementation based
on the Chameleon template compiler. It's largely compatible with
``zope.pagetemplate``.

Usage
-----

Load the package component configuration file (configure.zcml).

Performance
-----------

Casual benchmarks pegs it 16x more performant than the reference
implementations for Zope TAL and Genshi (using Python-expressions).

Compiler notes
--------------

The compiler is largely compatible with the reference
implementation. The TAL implementation is based on the 1.4 language
specification.

Some notable changes:

1. Tuple unpacking is allowed when defining variables:

      tal:define="(a, b, c) [1, 2, 3]"

2. Generators are allowed in tal:repeat statements. Note that the
   repeat variable is not available in this case.

      tal:repeat="i <some generator>"

3. Attribute-access to dictionary entries is allowed in
   Python-expressions, e.g.

      dictionary.key

   can be used instead of ``dictionary['key']``.

4. The default expression type is Python.

5. Genshi expression interpolation syntax is supported outside tags, e.g.

      <span>
         Hello, ${'world'}!
      </span>

      
.. _TAL: http://wiki.zope.org/ZPT/TALSpecification14


Development
-----------

If you want to use the code directly from trunk (recommended only for
development and testing usage), provide ``chameleon.zpt==dev`` as your
dependency.

svn://svn.zope.org/repos/main/Sandbox/malthe/chameleon.zpt/trunk#egg=chameleon.zpt-dev

Want to contribute? Join #zope3-dev on Freenode IRC.


