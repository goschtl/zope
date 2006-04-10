==========
Controller
==========

The controller is a single instance registered for an interface-key marker
registered as generic type.

    >>> registerDirective('''
    ... <generic:controller
    ...     interface="example.IBarMarker"
    ...     class='zope.generic.type.api.Object'
    ...     >
    ...    <initializer
    ...            interface='example.IOtherConfiguration'
    ...            handler='example.barInitializer'
    ...       />
    ...       <configuration
    ...           interface='example.IAnyConfiguration'
    ...        data='example.typedata'
    ...       />
    ... </generic:type>
    ... ''')
