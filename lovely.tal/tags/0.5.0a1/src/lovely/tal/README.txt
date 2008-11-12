==========
lovely.tal
==========

the lovely tal package is meant to contain new tal:expressions

TextFormatter
=============

option replace:
  takes a list of tuples, which characters or strings should be replaced by 
  what, e.g. ``replace python:[(origChar, repChar), (origChar2, repChar2), 
  ...]``

option allow:
  takes a list of html-tags which shall be allowed in the string e.g. ``allow 
  python:['a', 'br', 'ul', 'li']`` if this option is not set, the string is 
  restricted to contain no html-tags, therefor the ``< `` and ``>`` are 
  beeing replaced with ``&lt; ``, ``&gt;``

option allow-all:
  allow all html-tags in the string e.g. ``allow-all: 'True'``

option break-string:
  force the string to break after a given number of characters e.g. 
  ``break-string python:25`` breaks the string after a sequence of 25 
  characters not containing a linebreak
   						
option cut: 
  cuts a string to the given length

option attach: 
  works only together with option ``cut``, attaches the given string to the 
  expression, if this is longer than number of characters given in option 
  ``cut``

option urlparse:
  parsing of http:// or www. strings to hyperlinks, got a dictonary of parameters 
  e.g. urlparse python:{'rel':'nofollow','target':'_blank', allready existing
  anchor tags are extended with the parameters in the dictionary, image tags
  stay untouched in this whole parsing process

Example::
			
  <span tal:define="replace python:[('\n', '<br />')];
                    allow python:['a', 'br'];
                    break-string python:25;
                    urlparse python:{'rel':'nofollow','target':'_blank'};
                    cut python 25;
                    attach '...'"
        tal:content="structure textFormatter: view/description">Description</span>

Lets see if the TextFormatter does what we want him to.

We have to fake a context object to call the textformatter::

  >>> class Context(object):
  ...     vars = {}
  ...     def __init__(self, vars):
  ...         self.vars = vars
  >>> from lovely.tal.textformatter import TextFormatter
  >>> from zope.tales.expressions import simpleTraverse
  >>> from zope.app.pagetemplate.engine import TrustedZopeEngine
  >>> tf = TextFormatter('textFormatter', 'view/title', TrustedZopeEngine(), 
  ...                    simpleTraverse)
  >>> context = Context({})
  >>> tf._doFormat('<a href="#" name="foolink">foolink</a>', context)
  '&lt;a href="#" name="foolink"&gt;foolink&lt;/a&gt;'
  >>> tf._doFormat('<a href="#" name="foolink">foolink</a><br />'
  ...              '<form action="."><input type="text" /></form>', context)
  '&lt;a href="#" name="foolink"&gt;foolink&lt;/a&gt;&lt;br /&gt;&lt;form action="."&gt;&lt;input type="text" /&gt;&lt;/form&gt;'
  
if we provide an empty context, the textformatter translates all html-tags to 
``&lt; &gt;``

Option 'allow'
==============

We can allow certain html-tags in the text::

  >>> context = Context({'allow':['a']})
  >>> tf._doFormat('<a href="#" name="foolink">foolink</a><br /><form action="."><input type="text" /></form>', context)
  '<a href="#" name="foolink">foolink</a>&lt;br /&gt;&lt;form action="."&gt;&lt;input type="text" /&gt;&lt;/form&gt;'
  >>> context = Context({'allow':['a', 'br']})
  >>> tf._doFormat('<a href="#" name="foolink">foolink</a><br /><form action="."><input type="text" /></form>', context)
  '<a href="#" name="foolink">foolink</a><br />&lt;form action="."&gt;&lt;input type="text" /&gt;&lt;/form&gt;'
  >>> context = Context({'allow':['a', 'br', 'form']})
  >>> tf._doFormat('<a href="#" name="foolink">foolink</a><br /><form action="."><input type="text" /></form>', context)
  '<a href="#" name="foolink">foolink</a><br /><form action=".">&lt;input type="text" /&gt;</form>'

In the above example, still the content of the form tag is translated 
 
Lets try to write dirty html::

  >>> context = Context({'allow':['a', 'br', 'form']})
  >>> tf._doFormat('< a href="#" name="foolink">foolink</ a><br/>< form action="."><input type="text" /></form >', context)
  '&lt; a href="#" name="foolink"&gt;foolink&lt;/ a&gt;<br/>&lt; form action="."&gt;&lt;input type="text" /&gt;&lt;/form &gt;'

Since the a-tag and the form-tag are not valid html, they are translated, although we declared them to be allowed  
We get the same result if we do not allow them::

  >>> context = Context({'allow':['br']})
  >>> tf._doFormat('< a href="#" name="foolink">foolink</ a><br/>< form action="."><input type="text" /></form >', context)
  '&lt; a href="#" name="foolink"&gt;foolink&lt;/ a&gt;<br/>&lt; form action="."&gt;&lt;input type="text" /&gt;&lt;/form &gt;'

Option 'allow-all'
==================
 
We can allow all html-tags::

  >>> context = Context({'allow-all':True})
  >>> tf._doFormat('<a href="#" name="foolink">foolink</a><br /><form action="."><input type="text" /></form>', context)
  '<a href="#" name="foolink">foolink</a><br /><form action="."><input type="text" /></form>'

Option 'replace'
================

We can replace characters or strings, e.g. we would like to replace the '\n' character by '<br />'
to display the text properly::

  >>> context = Context({'replace':[('\n', '<br />')]})
  >>> tf._doFormat('das Schwein, \n das aus der Wueste kam', context)
  'das Schwein, <br /> das aus der Wueste kam'
  
we can also replace strings::

  >>> context = Context({'replace':[('\n', '<br />'), ('Schwein', 'Kamel')]})
  >>> tf._doFormat('das Schwein, \n das aus der Wueste kam', context)
  'das Kamel, <br /> das aus der Wueste kam'
 
Option 'break-string'
=====================

Another option is to break strings after a given number of characters n, in case there
was no break or '\s' in the last n characters::

  >>> context = Context({'break-string':8})
  >>> tf._doFormat('das Schwein, das aus der Wueste kam', context)
  'das<br />Schwein,<br />das aus<br />der<br />Wueste<br />kam'
  >>> context = Context({'break-string':8})
  >>> tf._doFormat('ein superlangerstring mit ein paar kurzen strings', context)
  'ein<br />superlan<br />gerstrin<br />g mit<br />ein paar<br />kurzen<br />strings'

Also multi line text works::

  >>> context = Context({'break-string':40})
  >>> res = tf._doFormat("""
  ... ein superlangerstring mit ein paar kurzen strings.
  ... 
  ... - another line
  ... 
  ... - another long string which needs to break
  ... and this needs to break twice because it is longer than 80 characters, hopefully it works
  ... """, context)
  >>> print res.replace('<br />', '\n')
  <BLANKLINE>
  ein superlangerstring mit ein paar
  kurzen strings.
  <BLANKLINE>
  - another line
  <BLANKLINE>
  - another long string which needs to
  break
  and this needs to break twice because it
  is longer than 80 characters, hopefully
  it works
  <BLANKLINE>
  >>> context = Context({'break-string':20, 'allow':['br']})
  >>> text = u'eins zwei drei vier fuenf sechs sieben,<br />'
  >>> text += u'in der Schule wird geschrieben,<br />'
  >>> text += u'in der Schule wird gelacht,<br />'
  >>> text += u'bis der Lehrer pitschpatsch macht!'
  >>> res = tf._doFormat(text, context)
  >>> print res.replace('<br />', '\n')
  eins zwei drei vier
  fuenf sechs sieben,
  in der Schule wird
  geschrieben,
  in der Schule wird
  gelacht,
  bis der Lehrer
  pitschpatsch macht!

the formatter considers tags as not to be part of the text, that means that
breaks aren't made inside tags (<...>)::

  >>> context = Context({'break-string':8, 'allow':['a']})
  >>> tf._doFormat('working at <a href="www.lovelysystems.com" name="lovelysystems">lovelysystems</a> is great!', context)
  'working<br />at<br /><a href="www.lovelysystems.com" name="lovelysystems">lovelysy<br />stems</a> is<br />great!'

Option 'cut'
============  

We can also cut strings to a given length::

Warning: cut will not check for HTML tags and will therefore cut in the middle
         of a tag which will make HTML unusable. Only use for plain text.

  >>> context = Context({'cut':20})
  >>> rendered = tf._doFormat('ein superlangerstring mit ein paar kurzen strings', context)
  >>> len(rendered)
  20

cut is done as the first operation. If it is combined with replace the
resulting string can be longer.

  >>> context = Context({'cut':20, 'replace':(('ein', 'Wrong case : ein'),)})
  >>> rendered = tf._doFormat('ein superlangerstring mit ein paar kurzen strings', context)
  >>> len(rendered)
  33


Option 'clear-html'
===================

  >>> context = Context({'clear-html':True})
  >>> tf._doFormat('Text <strong>containing</strong> HTML', context)
  'Text containing HTML'

This is done before "cut".

  >>> context = Context({'clear-html':True, 'cut':10})
  >>> tf._doFormat('Text <strong>containing</strong> HTML', context)
  'Text conta'

Option 'attach'
===============

and attach a string to the expression::

  >>> context = Context({'cut':20, 'attach':'...'})
  >>> tf._doFormat('ein superlangerstring mit ein paar kurzen strings', context)
  'ein superlangerstrin...'


Option 'softcut'
===============

the option softcut works together with cut and prevents cutting words::

  >>> context = Context({'cut':20, 'attach':'&hellip;', 'softcut':True})
  >>> tf._doFormat('ein superlangerstring mit ein paar kurzen strings', context)
  'ein&hellip;'

  >>> context = Context({'cut':25, 'attach':'&hellip;', 'softcut':True})
  >>> tf._doFormat('ein superlangerstring mit ein paar kurzen strings', context)
  'ein superlangerstring&hellip;'


Option 'urlparse'
=================

parse the urls in the expression:

    >>> context = Context({})
    >>> context = Context({'urlparse':{'rel':'nofollow','target':'_blank'},'allow':['a', 'br']})
    >>> tf._doFormat('<a href="http://www.lovelysystems.com/~auon/index.html">lovelysystems</a> rocks your zope', context)
    '<a href="http://www.lovelysystems.com/~auon/index.html" target="_blank" rel="nofollow">lovelysystems</a> rocks your zope'

    >>> tf._doFormat('ha ha hell yeah http://www.lovelysystems.com/ rocks your zope', context)
    '...<a href="http://www.lovelysystems.com/" target="_blank" rel="nofollow">http://www.lovelysystems.com/</a>...'

    >>> tf._doFormat('ha ha hell yeah www.lovelysystems.com/ rocks your zope', context)
    '...<a href="http://www.lovelysystems.com/" target="_blank" rel="nofollow">www.lovelysystems.com/</a>...'

    >>> tf._doFormat('ha ha hell yeah <img src="http://www.lovelysystems.com/image.jpg" /> rocks your zope', context)
    '...&lt;img src="http://www.lovelysystems.com/image.jpg" /&gt;...'
