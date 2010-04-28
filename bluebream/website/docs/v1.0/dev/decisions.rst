Technical Decisions
-------------------

- BlueBream is a "web framework".

- Shortening BlueBream as Bream or BB is acceptable.  As of now, the
  "BB" shortening is getting popular in community.

- There is only one public API exposed by "bluebream - the package"
  This API is an entry point provided by setuptools which use
  PasteScript::

    entry_points={
    "paste.paster_create_template":
        ["bluebream = bluebream.bluebream_base.template:BlueBream",
         ]}

- All the framework code is using "zope" or "zope.app" namespace
  packages. Although "bb" could be used as a namespace in future.

- "bluebream the project" consists of project templates.

- "bluebream_website" is the location where web content is stored.

- "bbkit" is where KGS infrastructure located.

- BlueBream 1.0 should provide an upgrade path from Zope 3.4 KGS.

- Any "shell command" required to be repeated after project creation
  should not be automated by the project template.

- Running ``bootstrap.py`` and ``buildout`` in the project should not
  be done during project template creation for the previous reason.
  Another supporting reason is the easiness of adding sources to
  version control systems.

- additional packages contained in namespaces such as "zc", "z3c", or
  others will be added in the future, but won't be part of the 1.0
  release.


.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
