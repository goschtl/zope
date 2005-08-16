==========================
Zope3 - I18n - Style Guide
==========================

------------
Introduction
------------

I18n samples ...

----------
Block text
----------

Use <tal:block> or <label> for translation strings, not span

::

  <span i18n:translate="msgid">blah</span>
  because it produces:
  <span>msgstr</span>
  with useless <span> elements that needlessly encumber the HTML output.
  
  <tal:block i18n:translate="msgid">A meaningful translation</tal:block>
  
  or

  <label i18n:translate="msgid">A meaningful translation</label>

-----------------------
Beware of empty <label>
-----------------------

::

  <label i18n:translate="msgid" />
  produces:
  <label />msgstr
  
  To produce <label>msgstr</label> one must write
  
  <label i18n:translate="msgid">A meaningful translation</label>
  
  <label i18n:translate="msgid">A meaningful translation</label>

---------
Messageid
---------

::

  Provide a meaningful translation message example in the template. Because a meaningful translation will help translators later on.
  
  <tal:block i18n:translate="msgid">A meaningful translation</tal:block>
  
  and NOT
  
  <tal:block i18n:translate="msgid"/> 

------------
Python rules
------------

Translate in Python if needed

Output that returns in page templates has to be translated in Python

::

  ...sample
