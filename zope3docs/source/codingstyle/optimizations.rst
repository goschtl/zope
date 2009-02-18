Although code optimization is not the primary goal in the current development
cycle of Zope3, here are some rules that should make further optimizations and the possible use of unicode less painful.

string module

  - Avoid to use the 'string' module. Instead use string methods. They are
    always much faster and share the same API with unicode strings !

  - Avoid slicing for checking if a string has a special prefix or suffix::

       NO:  if foo[:3]=='bar'...
       YES: if foo.startswith('bar'):

       NO:  if foo[-5:]=='.html'...
       YES: if foo.endswith('.html'):

    Using startwith()/endswith() is faster, cleaner and less error-prone.

usage of type()

  - constructs likes 'if type(obj) is type("")' should be replaced
    using isinstance()::

      NO:  if type(obj) is type(""):
      YES: if isinstance(obj, str):...

    When checking if a string is a string, keep in mind that
    it might be a unicode string too! The types module has
    the StringTypes type defined for that purpose. So a check
    for string or unicode string would look like that::

      from types import StringTypes  
      if isinstance(obj, StringTypes):...

    


<hr solid id=comments_below>


tim_one (May 24, 2002 10:14 am; Comment #1)  --
 Just noting that Python (probably 2.3) will introduce a common base class for str and unicode, so that isinstance will work without need of types.!StringTypes.
 
stevea (Jul 8, 2002 1:55 pm; Comment #2)  --
 Here or perhaps elsewhere, write something about not using '[]' as a marker object to detect default values when passed to queryNNNN functions. Instead, use an object(), as these don't get wrapped in security proxies.
 
