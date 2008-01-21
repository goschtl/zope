-------------------
 megrok.simpleauth 
-------------------

*Grok package for simple authentication*

==============
 Introduction
==============

This package provides a pre-configured PAU with PrincipalFolder,
InternalPrincipals (with easily extensible annotations) and SessionLogin(?),
and a set of views for user account creation, login, logout etc.

Calling megrok.setup inside your grok.App class configures all of the above
with sensible defaults, but the user schema can be extended and the views
overriden.


===============
 Basic outline
===============

from megrok import simpleauth
class Foo(grok.App, ...):
    simpleauth.setup([view_map], [user_schema])

view_map: A dictionary mapping default view names to custom ones for:

  * login
  * logout
  * join
  * user_search, user_listing
  * user_profile, user_edit

  Each one of these may be a string giving the new name for the view, or
  None to disable creation of that particular view.

user_schema: A schema (which extends simpleauth.IUser) defining user
attributes.
