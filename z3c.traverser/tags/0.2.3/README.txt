Traversers are Zope's mechanism to convert URI paths to an object of the
application. They provide an extremly flexible mechanism to make decisions
based on the policies of the application. Unfortunately the default traverser
implementation is not flexible enough to deal with arbitrary extensions (via
adapters) of objects that also wish to participate in the traversal decision
process.

The pluggable traverser allows developers, especially third-party developers,
to add new traversers to an object without altering the original traversal
implementation.
