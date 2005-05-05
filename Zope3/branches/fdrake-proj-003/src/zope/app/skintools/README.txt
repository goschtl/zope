======
README
======

The skintools package contains several reusable components which uses
the pagelet concept I've implemented several months ago. I hope
I can now show how easy pagelets can be used in the Boston skin.

Register the pagelets you like to a slot used in a skin. And to the
layer used in the skin.

This package only registres the interfaces used in the pagelets. 
See pagelet directive sample in configure.zcml.sample file in browser 
packages. 

The pagelets in the sub packages are strictly separated in data and layout
pagelets. This makes it resuable in other skins. You only have to register
our own layout pagelet.

Background
----------
Remember, pagelts are just another concept how ZPT macro's can be used.
If you understand how macros work, it's very easy to see, that pagelets
are just a generic lookup for ZPT's macro code. Since pagelets are  
registred on context, layers, views and slots (multiadapter), you can 
imagine how individual we can use this pagelets concept.

Example
-------

See zope.app.boston.slots.configure.zcml for a sample, which uses this 
skintool/pagelet pattern.

Tests
-----

Oh, well, what should we test? This are only views. I added some tests
in the zope.app.boston.browser.ftests.py. Perhaps we have to add some
tests here. This means we have to add a test skin, register this pagelets
and test if they renderd the HTML correct.
