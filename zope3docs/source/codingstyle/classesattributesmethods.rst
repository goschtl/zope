1. General

  For everything these pages are not mentioning, we are using the style
  specified by the Python Style Guide. Most of the code I have seen in Zope 3
  so far uses the "capatalize new words" instead of  "separate words by _" 
  style. Also, in general long names are more descriptive than short ones. 
  For example "speedOfLight" is much better than simply "c".


2. Classes

  Classes should *always* start with a capital letter. 
  Examples::

    Folder
    HTTPRequest
    HTTPViewRegistry
    ThisIsAVeryLongClassName


3. Attributes / Properties

   Attributes always start with a lower case letter. Boolean-type attributes
   should always form a true-false-question, typically using "has" or "is" 
   as prefix.
   Examples::
     
     title
     cssClass
     isRequired (boolean)

4. Methods

   Methods also should start with a lower case letter. The first word of a 
   method should always be a verb that describes the action.
   Examples::

     executeCommand()
     save()
     convertValueToString()

<hr solid id=comments_below>


gvanrossum (Jan 28, 2002 12:25 pm; Comment #1)  --
 An important guideline would be to explain when it is appropriate
 for a method or instance variable name to start with an underscore.
 
bwarsaw (May 24, 2002 11:10 am; Comment #2)  --
 Guido's right, it would be helpful to understand Jim's recommendations regarding leading underscores.  Here's mine, FWIW:
 
 - no leading underscores on public methods or attributes
 
 - a double leading underscore for names which describe private methods or attributes.
 
 - a single leading underscore for names which are not part of the public interface, but which might be of interest to subclasses.
 
 Yes, this means you should design for inheritance!  At the very least you need to decide what the contract is between subclasses and superclasses, and I typically represent these decisions with single-underscore names.  However, when in doubt, use single underscores instead of double underscores, otherwise it's a real pain to subclass.
 
klm (May 24, 2002 11:36 am; Comment #3)  --
 <pre>
 > bwarsaw (May 24, 2002 11:10 am; Comment #2)  --
 > [...]
 >  - a double leading underscore for names which describe private methods
 >    or attributes.
 >  
 >  - a single leading underscore for names which are not part of the public
 >    interface, but which might be of interest to subclasses.
 </pre>
 
 I do **not** think it's a good idea to use a name-mangling double underscore except when you actually *expect* that subclasses will need distinct but identically named methods (and ones which will not directly call the superclass versions, of course).  (Maybe double underscore is also useful to protect some critical class invariant that uninformed use of the method would betray, but even there a decent warning in the code should suffice.)
 
 Why the emphatic tone?  I have had grief developing against code where the other developer had used double underscores because *they* weren't going to use the method in a subclass - preventing me when i legitimately needed to do so.  
 
 Further, double underscores impede interactive debugging - arriving in a context where things are already going wrong, and needing to scramble to uncover the mangling rule so you can invoke an obscured method, compounds the pain of the moment - and breaks pdb-track, besides.
 
 Please, avoid idealistic use of double-underscores - a single underscore is sufficient to signal intent, and does not present obstacles that are often unnecessary and sometimes counterproductive.
 
