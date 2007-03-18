megrok.viewlet
==============

This is a proof of concept of a way to support portlets in Grok. 
The code is experimental.


This package provides two things:

1. Grokish viewlet and viewletmanager classes to let you create 
   viewletmanagers and viewlets without ZCML. This is my first attempt of 
   making Grokkers, so I expect that this code needs some cleanup, but 
   otherwise I think the basic ideas are useable.

   Also, there is currently no way to set the interface and layer for which 
   the viewlet should be displayed. This needs to be added.

2. A new publication object, that will not call the published object directly.
   Instead, it will call a main template (currently hardcoded in this proof
   of concept, but it should probably be looked up through layers instead)
   that will simply call a bunch of viewlet managers and render them.
   The content of the object is instead rendered by a content viewlet by the
   main_content viewlet manager.

regebro@gmail.com
