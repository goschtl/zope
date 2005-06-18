===========================
Welcome to the Zope3 source
===========================

This file provides some basic hints for people developing Zope3 software.
There is more developer info in the Zope 3 Wiki:

  http://dev.zope.org/Zope3/Zope3DeveloperInfo

For information about the current release, see ``doc/CHANGES.txt``.

Zope 3 is now a stable platform on which production systems can and are built.


Building and running tests
--------------------------

See ``INSTALL.txt`` which Python version is required for Zope 3.

In the top-level ``Zope3`` directory, you should find a script called
setup.py.  Run it to build the extension modules needed by Zope.  Example::

  # cd Zope3
  # python setup.py -q build_ext -i

On a unix variant, you can just type: ``make``

On Windows, if you downloaded the binary distribution, this has already been
done for you (since the compiler we use on Windows isn't free).

Zope 3 includes unit tests based on the Python unittest module.  If you check
in changes, you should verify that all the tests succeed before you commit
changes.

To run all the tests, use the script test.py::

  # python test.py -v

Use ``test.py -h`` for usage.  The test script can run selected tests, stop
after the first error, run the tests in a loop, etc.


Starting Zope 3
---------------

Before running Zope, you need to create one or more bootstrap users.  Copy the
file ``sample_principals.zcml`` to ``principals.zcml``, and edit the result to
your needs.  Make sure you change the passwords.

To run Zope just run the ``z3.py`` script::

  # python z3.py

Or, if you use make on Unix, you can run::

  # bin/runzope

This will run Zope on port 8080.  Visit the url::

  http://localhost:8080/manage

This goes to the Zope 3 default management interface.  Note that
this release of Zope 3 requires recent versions of Mozilla or IE. Note that
other modern browsers, such as Konqueror and Safari, also mostly work well.

If you insist on using an older browser (or a text-based browser)
you can use the basic Zope 3 skin by putting ``++skin++Basic`` after
the server part of the URL::

  http://localhost:8080/++skin++Basic/manage

See ``doc/INSTALL.txt`` for more information.


Finding out how to develop new content types
--------------------------------------------

There are several documentation sources out there. As of this writing two
books have been published and much online documentation is available:

  - Zope 3 comes with an extensive API documentation tool, which also compiles
    many of the package-specific README files. Once you start up Zope, simply
    go to:

      http://localhost:8080/++apidoc++

  - `Zope 3 Developer's Handbook`:

    * On Paper: http://www.samspublishing.com/title/0672326175

    * Online: http://dev.zope.org/Zope3/Zope3Book

  - `Web Component Development with Zope 3`:

    * On Paper: http://www.springeronline.com/sgw/cda/frontpage/0,11855,1-102-22-35029949-0,00.html

    * Online: http://www.worldcookery.com

  - The developers tutorial at:

    http://dev.zope.org/Zope3/ProgrammerTutorial

  - Ask questions on the mailing lists and chat channels:

    * Zope 3 Development: ``http://lists.zope.org/mailman/listinfo/zope3-dev``

    * Zope 3 Users: ``http://lists.zope.org/mailman/listinfo/zope3-users``

    * IRC channel `#zope3-dev` on irc.freenode.net

  - To keep up with the latest changes, the commits mailing list
    ``http://lists.zope.org/mailman/listinfo/zope3-checkins``


Acknowledgements
----------------

Zope 3 is a Zope Community effort.  There are many Zope 3 contributors without
whom there wouldn't be a Zope 3.

See the ``doc/CREDITS.txt`` file for details.

Much thanks folks!
