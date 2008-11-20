Testing Utilities
=================

Layers
------

Some basic layers useful for making test setups.

    >>> import os.path
    >>> from van.testing.layer import zcml_layer, null_layer

A zcml layer which sets up and tears down a zcml test harness (but is much
simpler than that provided with zope.app.functional):

    >>> class ZCMLLayer:
    ...     zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
    >>> zcml_layer(ZCMLLayer)

Some default layers are provided for use with zope.testing, a "null" layer that
specifically does nothing. This is useful for layers which inherit from other
layers but where you don't want setup/teardown functions run twice (is this a
zope.testing bug?):

    >>> class ExampleNullLayer(ZCMLLayer):
    ...     pass
    >>> null_layer(ExampleNullLayer)
