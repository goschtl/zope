This is an area for *throw-away* prototypes.

It is *important* to note that the practices for throw-away and
evolutionary prototypes are totally different.

For a throw-away prototype, the goal is to explore a problem
you don't understand by trying things out. It's pointless to
document and write tests.  It would be counter productive. It doesn't
really matter what the code looks like.  Speed of implementation
is important, because you want to try things out quickly. You don't
want to waste time thinking about apis, etc.

When you understand a problem, or at least think you do, you can
start writing the evolutionary prototye (a.k.a. the final system ;).
You may still throw it away, or refactor it, but the expectation
is that what your working on will evolve into something of value.
At this point, it's time to start doing things right. It's time to
start following Zope 3 practices.  At this point, the code should
move into the Zope 3 tree, or into a separate project. 

If you want to experiment here, create a subdirectory with a name that
is descriptive and includes your (or your project's) name
(e.g. jim-zope-gui, zc-teleportation).
