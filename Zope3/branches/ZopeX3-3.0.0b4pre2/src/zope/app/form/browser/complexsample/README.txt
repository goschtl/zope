Sample complex widget
---------------------

This directory contains an example of a *complex* widget (as opposed
to a *composite* widget).  The following files are provided:

complexsample.py
    Concrete widget implementation.

configure.zcml
    Configuration connecting the widgets with the vocabulary and query
    objects implemented in this package.

interfaces.py
    Interfaces for the vocabulary and query objects implemented in
    vocabulary.py.

vocabulary.py
    Dummy sample vocabulary and query objects that demonstrate the
    kind of query behaviors the sample widget expects.

widgetapi.py
    Alternate base implementation of the `IBrowserWidget` interface.
    This completely bypasses the implementation from the
    `zope.app.form.browser.widget` module, and is really designed for
    use with widgets of the sort demonstrated in this package.
