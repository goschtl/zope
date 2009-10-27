User preferences
================

The ``z3ext.preferences`` package implements a method to easily add custom
principal preferences in a single way, automatically providing browser menus
and edit forms for these preferences.

The preferences are organized in hierarchical way to ease navigation between
them, so each group of preferences can have multiple children groups. Those
"preference groups" is what a developer creates.  

Though the package is made very flexible, the basic usage is very simple.

Basic usage
-----------

If you simply want to store some user-specific data and make it automaically
editable by user, you need to:

1. Define a preference group schema (just like any zope schema - an interface
   with zope.schema fields defined in it). Example::
    
     class ISimpleProfile(zope.interface.Interface):
     
         birthDate = Date(title=u'Birth Date', required=True)
         signature = Text(title=u'Signature', required=False)
    
2. Register it using the ``z3ext:preferenceGroup`` ZCML directive. Example::
    
     <z3ext:preferenceGroup
       id="simpleprofile"
       title="Simple Profile"
       schema=".interfaces.ISimpleProfile"
       />

The ZCML directive have three required arguments: id, title and schema. While
``title`` and ``schema`` are self-explanatory, the ``id`` argument have its
catches. First, as it's clear from the name, it should be unique identifier
of the group. Second, because preference groups are hierarchical, dot symbol
in the id has a special meaning.

In the example above, we don't have any dots in the id. It means that this
preference group will be added to the root group, it can be thinked of as
the "top-level" group. However, if we will create another preference group
with, for example, "simpleprofile.moreinfo" as the id, the new group is added
as a child to our "simpleprofile" group and it's menu item will be rendered
as a sub-menu item under the "Simple Profile".

There is no restriction on the depth of preference group nesting, but remember
that you should always register parent groups before registering child groups.

After registering the preference group, a principal (IPrincipal object)
can be adapted to an interface used as a preference group schema (which is
ISimpleProfile in our examples above) and the values for fields defined in
the schema can be get and set. The preferences mechanism handles storage of
that values itself.

The preference groups can also be looked up as a named utility providing
``z3ext.preferences.interfaces.IPreferenceGroup`` interface using the group id
as a name. However, those groups are not bound to any principal and their
attributes can not be got or set. To bind an unbound group to a principal, you
can use the ``__bind__`` method, passing the principal object as the argument.

.. note::

   The preference group objects are not persistent and only those attributes
   will be stored by default that are defined in the preference group schema.


The browser UI for editing principal preferences are available as view named
"preferences" for the site objects (objects providing 
``zope.app.component.interfaces.ISite`` interface). So if your site root is at
"http://yoursiteurl.com", the preferences UI will be available at
"http://yoursiteurl.com/preferences". 

Advanced usage
--------------

Things to describe:

* all zcml directive arguments
* security settings for preference groups
* availability testing
* custom preference groups classes
* custom browser views for preference groups (including empty schema preference
  group hint). 
* custom data storage adapters
 