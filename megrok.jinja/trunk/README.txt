Introduction
============

megrok.jinja makes it possible to use Jinja2 templates in Grok.

For more information about Grok and Jinja2 visit:

- http://grok.zope.org/
- http://jinja.pocoo.org/

Requirements
------------

- Grok v1.0a or later. Tested with Grok v1.0a2.
- Jinja v2.1.1 or later. Tested with Jinja v2.1.1
- PyYAML v3.08 or later. Tested with PyYAML v3.08
- simplejson v1.7.1 or later. Tested with simplejson v1.7.1

Installation
------------

To use the Jinja2 templates within Grok, megrok.jinja must be first
installed as an egg, and its ZCML included. After using grokproject,
amend the setup.py to look like this::

    install_requires=[''setuptools',
                      'grok',
                      'megrok.jinja',
                      # Add extra requirements here
                      ],

Then include megrok.jinja in your configure.zcml. It should look
something like this::

    <configure xmlns="http://namespaces.zope.org/zope"
               xmlns:grok="http://namespaces.zope.org/grok">
      <include package="grok" />
      <include package="megrok.jinja"/>
      <grok:grok package="." />
    </configure>

Rerun buildout (bin/buildout), giving you something like:

    Getting distribution for 'megrok.jinja'.
    Got megrok.jinja 0.1

That's it. You can now place Jinja2 templates (with the `.jinja` extension)
into any template directory used within your project.

Jinja2 Environment
------------------

megrok.jinja creates an Environment using `jinja2.ext.i18n` extension and overrides
the globals variables `_` and `gettext` in order to use custom functions to resolve
translations. It also set the global variable `provider` as a function to resolve
the call to a content provider (viewlet manager).

For more information about Jinja2 Environment and Global variables visit:

- http://jinja.pocoo.org/2/documentation/api#high-level-api
- http://jinja.pocoo.org/2/documentation/api#the-global-namespace

With the extensions added you are able to use
 - zope.i18n messages factory
 - content providers like viewlets

To translate your templates, just register your translations domain and then
you can write::

    {% set i18n_domain='test_domain' %}

    {{ _('some-msgid')}}

Also it's possible to use the {%trans%} tag::

    {% set i18n_domain='test_domain' %}

    {% trans %}
    Whatever you may want to translate.
    {% endtrans %}


It's important to note that, `messages` created in python classes
won't be translated like in Zope Page Templates.

If you write:

view.py::

    from zope import i18nmessageid
    _ = i18nmessageid.MessageFactory('some.domain')

    class Something(grok.View):
        def update(self):
            self.msg = _('Some msg id')

view.jinja::

    {{ view.msg }}

You will always get 'Some msg id'. What you do could write is:

view.py::

    class Something(grok.View):
        def update(self):
            self.msg = 'Some msg id'

view.jinja::

    {% set i18n_domain='some.domain' %}

    {{ _(view.msg) }}

Note that megrok.jinja uses the `translate` function from
zope.i18n.interfaces.ITranslationDomains, so using::

    {{ _('msg_id') }}

you can pass all the parameters accepted by `translate`::

    {{ _('msg_id', domain='another_domain', target_language='es') }}

If you want to call some content provider named 'manager', just write::

    {{ provider('manager') }}

About `.json` extension and PyYAML
----------------------------------

For more information about PyYAML visit:
- http://pyyaml.org/wiki/PyYAML

megrok.jinja allows you to write templates with `.json` extension and
inside it, you are able to mix the Jinja2 syntax with PyYAML.

First, megrok.jinja will try to parse the template using Jinja2
and the result it's passed to the PyYAML loader. If PyYAML it's
able to load the string passed, the result it's returned with simplejson.dumps

If you write this in a template with `.json` extension::

    dicts :
       - key1 : some_text
       - key2 : {{ 'Some Jinja2 expression' }}
         {% set l = ['3','4'] %}
         {% for v in l %}
       - {{ 'key-' + v }} : whatever {{ v }}
         {% endfor %}

You will get the next JSON::

     {"dicts": [{"key1": "some_text"},
                {"key2": "Some Jinja2 expression"},
                {"key-3": "whatever 3"},
                {"key-4": "whatever 4"}]}


Authors
-------

- Santiago Videla

