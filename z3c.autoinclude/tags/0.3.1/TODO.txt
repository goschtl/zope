in no particular order, some notes on things that I think ought to happen to this code:

 * Profiling.  As far as I know, none has been done, and I expect that the code is *very* slow. Then, obviously, optimizations should be considered.
 * Documentation.  It's still fairly poor; I think the whole damn thing is just so abstract that I can't figure out how to talk about it.
 * May as well figure out how to make a PasteScript template to auto-generate the entry point.
 * Better debugging tools/APIs: to see what will be autoincluded, turn on and off autoinclusion for individual packages, and freeze a ZCML file capturing autoinclusion information a la pip.

One day I also want to add another directive to autoinclude subpackages' ZCML; this is a frequent annoyance for me (see https://svn.openplans.org/svn/opencore/trunk/opencore/configuration/configure.zcml for an illustrative example)
