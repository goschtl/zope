================
Z3C I18N Package
================

This package contains various i18n related convinience modules.

Translation Domains
-------------------

The following translation domains are registered based on the
`zope.i18n.locales` package:

``z3c.i18n.iso.languages``: Translates all available languages

``z3c.i18n.iso.territories``: Translates all available terrritories

Vocabularies
------------

Based on the translation domains mentioned above, there are two
vocabularies registered. The terms of these vocabularies have a
``Message`` as title with the according translation domain.

``z3c.i18n.iso.languageVocabularyFactory``: Contains all languages defined.

``z3c.i18n.iso.territoryVocabularyFactory``: Contains all territories defined.



