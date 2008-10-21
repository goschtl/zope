Introduction
============

This skin is a derivative of the zope.app.boston.Boston skin, which
supports pagelets, forms and javascript forms.

Usage:


It includes the information needed to configure itself. To add it
to your configuration;

    1.  Add it to your buildout...

        eggs=...
            z3c.boston

    2.  To use the skin, you can use a traversal adapter:

        http://localhost:8080/++skin++z3c_boston/index.html

    3.  To configure this as your default skin, add this line to your
        site.zcml file:

        &lt;includeOverrides package="z3c.boston" file="default_skin.zcml" /&gt;

