Overview
========

To translate any text, we must be able to discover the source domain of the
text. A source domain is an identifier that identifies a project that produces
program source strings. Source strings occur as literals in python programs,
text in templates, and some text in XML data. The project implies a source
language and an application context.

We can think of a source domain as a collection of messages and associated
translation strings.

We often need to create unicode strings that will be displayed by separate
views. The view cannot translate the string without knowing its source domain.
A string or unicode literal carries no domain information, therefore we use
messages. Messages are unicode strings which carry a translation source domain
and possibly a more specific translation context. They are created by a message
factory. The message factory is created by calling ``MessageFactory`` with the
source domain.

This package provides facilities for *declaring* such messages within program
source text; translation of the messages is the responsibility of the
'zope.i18n' package.

Relationship to zope.i18nmessageid
----------------------------------

This packages has a number of semantic differences to zope.i18nmessageid.

Instead of advertising to use the msgid as a cryptic unique id for
disambiguation of messages in the same domain, we provide an optional context
attribute to do the same. This follows more modern gettext semantics and works
with the msgctxt feature.

So instead of doing::

  Message(u'some-id', default=u'Some text')

You write::

  Message(u'Some text', context=u'some-id')

but most often you will not provide a context at all::

  Message(u'Some text')

Messages created by this package also don't try to provide immutability or care
about security concerns. This allows the package to avoid a C dependency. Use
it with care in environments using zope.security proxies.
