
Notes and thoughts
-------------------

In previous API, hasValidInput() provided not only that value was valid, but
also that the widget had been rendered.

In the new API, that same information is conveyed by a non-None hasState() and 
a None value in error.

Old API's hasInput() is equivalent to new API's hasState()


---------------------

TODO for zope.widget:
  
 - Write simple widget to implement
 - Write doctest, include descriptions of cases below
 - Check in on branch
 - (Write proposal)
 
Standard widget use cases:
 
   - initial draw
   - subsequent draw; use request
   - subsequent draw; ignore request (force value)
   - initial or subsequent draw from state object
   

sample pseudocode:

first two use cases
-----
w = Widget()
w.initialize(prefix)
if not w.hasState():
    w.setValue(value)


third use case
------
w = Widget()
w.initialize(prefix, value)

fourth case
----
w = Widget()
w.initialize(prefix, state=obj)
