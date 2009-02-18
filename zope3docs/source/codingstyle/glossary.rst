This is a list of some common words that should have the same meaning throughout Zope.  It is not exhaustive.

  'key' -- See NamesKeysAndIds

  'id' -- See NamesKeysAndIds

  'manager' --
    1. A user that configures components, such as a SiteManager.  2. An object that performs through the web configuration, such as a ServiceManager (which allows site managers to configure services.)

    Generally, the word 'manager' is inappropriate for objects that don't perform through-the-web configuration.  For example, global "service services" are not configurable through the web, but they were once called "service managers", and have now been renamed, since the name caused confusion with through-the-web configurable service managers.

  'name' -- See NamesKeysAndIds

