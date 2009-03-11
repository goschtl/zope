===============
z3ext.formatter
===============

This package adds extensible tales expression for various formatters.
You can change formatter setting per site basis (z3ext.controlpanel).

For configure default settings, add following code to zope.conf

<product-config z3ext.formatter>
  timezone UTC
  timezoneFormat 2
  principalTimezone true
</product-config>

Values for timezoneFormat are:
    1: No timezone
    2: Number of hours
    3: Timezone name

We need register controlpanel configlet

  >>> from zope.configuration import xmlconfig
  >>> context = xmlconfig.string("""
  ... <configure xmlns:z3ext="http://namespaces.zope.org/z3ext"
  ...      i18n_domain="z3ext.formatter">
  ...    <include package="z3ext.controlpanel" file="meta.zcml" />
  ...  <z3ext:configlet
  ...     name="formatter"
  ...     schema="z3ext.formatter.interfaces.IFormatterConfiglet"
  ...     title="Portal formatters"
  ...     description="Configure portal formatters."/>
  ... </configure>""")

We'll try emulate <product-config z3ext.formatter>

  >>> from zope.app.appsetup import product
  >>> product._configs['z3ext.formatter'] = {
  ...   'timezone': u'UTC', 'timezoneFormat': '2', 'principalTimezone': 'true'}

Let's check this

   >>> product.getProductConfiguration('z3ext.formatter')
   {'timezone': u'UTC', 'timezoneFormat': '2', 'principalTimezone': 'true'}


Usually initFormatter() function is colled during IDatabaseOpenedEvent event,
we simply call it directly:

   >>> from z3ext.formatter.config import initFormatter
   >>> initFormatter(None)

Now we can get IFormatterConfiglet utility

   >>> from zope.component import getUtility
   >>> from z3ext.formatter.interfaces import IFormatterConfiglet

   >>> configlet = getUtility(IFormatterConfiglet)

Setup request

   >>> from zope import interface
   >>> from zope.publisher.browser import TestRequest
   >>> from zope.annotation.interfaces import IAttributeAnnotatable

   >>> request = TestRequest(environ={'HTTP_ACCEPT_LANGUAGE': 'en'})
   >>> interface.directlyProvides(request, IAttributeAnnotatable)

   >>> from pytz import UTC
   >>> from datetime import date, datetime, timedelta


DateTime formatter
------------------

   >>> from z3ext.formatter.tests import ZPTPage
   >>> page = ZPTPage()
   >>> page.pt_edit(u'''
   ... <html>
   ...   <body>
   ...     <tal:block tal:content="formatter:dateTime,short:options/now" />
   ...     <tal:block tal:content="formatter:dateTime,medium:options/now" />
   ...     <tal:block tal:content="formatter:dateTime,long:options/now" />
   ...     <tal:block tal:content="formatter:dateTime,full:options/now" />
   ...     <tal:block tal:content="formatter:dateTime:options/now" />
   ...   </body>
   ... </html>''', 'text/html')

   >>> dt = datetime(2007, 1, 1, 0, 0, 0, tzinfo=UTC)
   >>> dt
   datetime.datetime(2007, 1, 1, 0, 0, tzinfo=<UTC>)

By default we use UTC timezone for output:

   >>> print page.render(request, now=dt)
   <html>
     <body>
       1/1/07 12:00 AM
       Jan 1, 2007 12:00:00 AM
       January 1, 2007 12:00:00 AM +000
       Monday, January 1, 2007 12:00:00 AM +000
       Jan 1, 2007 12:00:00 AM
     </body>
   </html>


If datetime object doesn't contain timezone information, UTC is used

   >>> print page.render(request, now=datetime(2007, 1, 1, 0, 0))
   <html>
     <body>
       1/1/07 12:00 AM
       Jan 1, 2007 12:00:00 AM
       January 1, 2007 12:00:00 AM +000
       Monday, January 1, 2007 12:00:00 AM +000
       Jan 1, 2007 12:00:00 AM
     </body>
   </html>


Now let's chane timezone to US/Pacific, we change only time zone 
not datetime value

   >>> configlet.timezone = 'US/Pacific'

   >>> print page.render(request, now=dt)
   <html>
     <body>
       12/31/06 4:00 PM
       Dec 31, 2006 4:00:00 PM
       December 31, 2006 4:00:00 PM -800
       Sunday, December 31, 2006 4:00:00 PM -800
       Dec 31, 2006 4:00:00 PM
     </body>
   </html>


Now we can change timezone format to 3 (Timezone name)

   >>> configlet.timezoneFormat = 3
   
   >>> print page.render(request, now=dt)
   <html>
     <body>
       12/31/06 4:00 PM
       Dec 31, 2006 4:00:00 PM US/Pacific
       December 31, 2006 4:00:00 PM -800
       Sunday, December 31, 2006 4:00:00 PM US/Pacific
       Dec 31, 2006 4:00:00 PM US/Pacific
     </body>
   </html>


We also can redefine timezone for principal if we use principalTimezone true

   >>> from pytz import timezone
   >>> from zope import interface, component
   >>> class IPrincipal(interface.Interface):
   ...   pass

   >>> class Principal:
   ...     interface.implements(IPrincipal)
   ...
   ...     def __init__(self, id):
   ...         self.id = id
   ...         self.groups = []

   >>> @component.adapter(IPrincipal)
   ... @interface.implementer(interface.common.idatetime.ITZInfo)
   ... def getTimezone(prin):
   ...   if prin.id == 'user1':
   ...     return timezone('Europe/Paris')
   ...   elif prin.id == 'user2':
   ...     return timezone('Asia/Almaty')
   >>> component.provideAdapter(getTimezone)

   >>> request.setPrincipal(Principal('user1'))
   >>> print page.render(request, now=dt)
   <html>
     <body>
       1/1/07 1:00 AM
       Jan 1, 2007 1:00:00 AM Europe/Paris
       January 1, 2007 1:00:00 AM +100
       Monday, January 1, 2007 1:00:00 AM Europe/Paris
       Jan 1, 2007 1:00:00 AM Europe/Paris
     </body>
   </html>

   >>> request.setPrincipal(Principal('user2'))
   >>> print page.render(request, now=dt)
   <html>
     <body>
       1/1/07 6:00 AM
       Jan 1, 2007 6:00:00 AM Asia/Almaty
       January 1, 2007 6:00:00 AM +600
       Monday, January 1, 2007 6:00:00 AM Asia/Almaty
       Jan 1, 2007 6:00:00 AM Asia/Almaty
     </body>
   </html>

   >>> request.setPrincipal(None)


fancyDatetime formatter
-----------------------

   >>> now = datetime.now(UTC)

   >>> fpage = ZPTPage()
   >>> fpage.pt_edit(u'''
   ... <html>
   ...   <body>
   ...     <tal:block tal:content="formatter:fancyDatetime:options/now" />
   ...     <tal:block tal:content="formatter:fancyDatetime,short:options/now" />
   ...     <tal:block tal:content="formatter:fancyDatetime,medium:options/now" />
   ...     <tal:block tal:content="formatter:fancyDatetime,full:options/now" />
   ...   </body>
   ... </html>''', 'text/html')

Today's datetime

   >>> today = now - timedelta(hours=1)

   >>> print fpage.render(request, now=today)
   <html>
     <body>
       Today at ...
       Today at ...
       Today at ...
       Today at ...
     </body>
   </html>


Yesterday's datetime

   >>> yesterday = now - timedelta(hours=25)

   >>> print fpage.render(request, now=yesterday)
   <html>
     <body>
       Yesterday at ...
       Yesterday at ...
       Yesterday at ...
       Yesterday at ...
     </body>
   </html>


Default timezone is UTC

   >>> now = datetime.now(UTC)
   >>> print fpage.render(request, now=now)
   <html>
     <body>
       Today at ...
       Today at ...
       Today at ...
       Today at ...
     </body>
   </html>


Date formatter
--------------

   >>> datepage = ZPTPage()
   >>> datepage.pt_edit(u'''
   ... <html>
   ...   <body>
   ...     <tal:block tal:content="formatter:date:options/today" />
   ...     <tal:block tal:content="formatter:date,short:options/today" />
   ...   </body>
   ... </html>''', 'text/html')

   >>> d = date(2007, 1, 1)
   >>> d
   datetime.date(2007, 1, 1)

   >>> print datepage.render(request, today=d)
   <html>
     <body>
       Jan 1, 2007
       1/1/07
     </body>
   </html>


Also you can get formatter from python code

   >>> from z3ext.formatter.utils import getFormatter
   >>> formatter = getFormatter(request, 'dateTime', 'full')
   >>> formatter.format(dt)
   u'Sunday, December 31, 2006 4:00:00 PM US/Pacific'

We will get FormatterNotDefined if formatter is unknown

   >>> getFormatter(request, 'unknown')
   Traceback (most recent call last):
   ...
   FormatterNotDefined: ...

Wrong format, we should add path expression

   >>> errpage = ZPTPage()
   >>> errpage.pt_edit(u'''
   ...     <tal:block tal:content="formatter:unknown" />''', 'text/html')
   >>> print errpage.render(request)
   Traceback (most recent call last):
   ...
   PTRuntimeError: ...

Unknown formatter

   >>> errpage = ZPTPage()
   >>> errpage.pt_edit(u'''
   ...     <tal:block tal:content="formatter:unknown:opitons/now" />''', 'text/html')
   >>> print errpage.render(request)
   Traceback (most recent call last):
   ...
   FormatterNotDefined: unknown


Custom formatter
================

We should define formatter factory and formatter itself
Let's implement formatter that accept string and currency name and 
format as currency. Format of TALES expression whould be as 
'formatter:<formatter name>,<formatter var1>,<formatter var2>,...:<path expression>'
<formatter name> is name of adapter that adapts IHTTPRequest to IFormatterFactory
also expression will pass <formatter var[1-...]> as args to factory.

   >>> from z3ext.formatter.interfaces import IFormatter, IFormatterFactory

Here code of formatter:

   >>> class MyFormatter(object):
   ...    interface.implements(IFormatter)
   ...
   ...    currencies = {'usd': '$', 'euro': 'Eur'}
   ...
   ...    def __init__(self, request, *args):
   ...       self.request = request
   ...       self.currency = self.currencies[args[0]]
   ...
   ...    def format(self, value):
   ...       return '%s %s'%(value, self.currency)

Now we need formatter factory:

   >>> class MyFormatterFactory(object):
   ...    interface.implements(IFormatterFactory)
   ...
   ...    def __init__(self, request):
   ...        self.request = request
   ...
   ...    def __call__(self, *args, **kw):
   ...        return MyFormatter(self.request, *args)

Now we need register factory as named adapter for IHTTPRequest

   >>> from zope.component import provideAdapter
   >>> from zope.publisher.interfaces.http import IHTTPRequest

   >>> provideAdapter(MyFormatterFactory, \
   ...   (IHTTPRequest,), IFormatterFactory, name='currency')

Now we can use formatter

   >>> page = ZPTPage()
   >>> page.pt_edit(u'''<tal:block tal:define="value python:121.04">
   ... <tal:block tal:content="formatter:currency,usd:value" />
   ... <tal:block tal:content="formatter:currency,euro:value" />
   ... </tal:block>''', 'text/html')

   >>> print page.render(request)
   121.04 $
   121.04 Eur
