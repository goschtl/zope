==============
PageletChooser
==============

It's really helpfull if you understand how page template macros 
get rendered in the metal:use-macro tag.

The PageletChooser is a enhancement for the MacroCollector
adapter which can lookup paelet macros for a given name
related to the instance. If you use it, you will get a 
view on the instance for to choose which pagelt macro will
be used. You can select a pagelet macro name from the different 
registred pagelets.

The adapter PageletChooser registred for IChooseablePagelets
can lookup and return a pagelet name for a given key. 
The PageletChooser adapter requires a IPageletNameManager adapter 
for to get a object which provides the property with the property
where we whant lookup the mapped name. 

Use case
--------

Say you have a skin with a first level navigation with a image which
requieres a image map driven by javascript. 

What we can do with the PageletChooser is:

First add a page template and image with the image map and register
this page template as a pagelet 'called firstlevel_macro_10'.

Add a interface inherited called 'IFirstLevelPagelets' from 
IChooseablePagelets which is inherited from IPageletSlot. This means you 
are defining a pagelet slot interface. 

Add a index.html view and use the pagelet: tag with the interface
'IFirstLevelPagelets' like:
<metal:block tal:define="global chooser ...
  ...pagelet:zope.app.demo.pageletchooser.interfaces.IFirstLevelPagelets">
  <tal:block metal:use-macro="chooser/firstlevel" />
</metal:block>

Register a content type which implements the schema 'IChooseablePageletNames'
and register a adapter which supports the  'IPageletNameManager' schema.
The 'IPageletNameManager' adapter has to support your pagelet macro
names as field properties. In our use case 'firstlevel'.

For to let you change the pagelet macro names on the contentn type,
you need some different components.

Register a PageletNamesVocabulary vocabulary called 'firstlevelnames'.
Declare also your layer, view and slot interface in the vocabulary ZCML
directive. This vocabulary can lookup the macro names of pagelets registred
on this layer, views and slots. Use this vocabulary in the property fields
of your IPageletNameStore interface as a Choice field. This will render the 
fields as a selectbox where you can select on of the registred pagelet macro
names. Use this vacabulary for the schema of your pagelet names.

Define Choice fields in the schema 'IFirstLevelPagelets'. 
The name of the field is the key of the pagelt where you will lookup in a 
page template. In our example the field is called 'firstlevel' which is 
useing the vocabulary "firstlevelmacronames".

Add another adapter on your content type supporting the 'IFirstLevelPagelets' 
schema. This adapter is setting and getting the mapped names of the 
property field 'firstlevel'.

So, that's enough for this moment. For a real example look at the package 
zope.app.demo pageletchooser.

Feel free to enhance or change this README for a better understanding.


Glosary:
--------

Pagelet name or macro name:

Pagelet names are page template macro names which can be rendered 
in the metal:use-macro tag. A pagelet name is the name of the macro.
This means if you register a pagelet with the name 'firstlevel_macro_10' 
the page template must contain a macro called 'firstlevel_macro_10' like:
'define-macro="firstlevel_macro_10"'

PageletChooser:

Can lookup pagelet names on objects via the adapter IPageletNameManager
A PageletChooser is a replacement for the MacroCollector which is used
as a IMacroCollctor adapter.
