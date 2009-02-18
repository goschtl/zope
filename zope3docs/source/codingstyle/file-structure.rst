Here I would just like to look at Python Source Files. These files should always contain the most actual license comment at the top followed by the
module documentation string. The doc string will contain a reference about 
its CVS status in the first line; then the documentation follows. 
Here is the template::

  ##############################################################################
  #
  # Copyright (c) 2002 Zope Corporation and Contributors. 
  # All Rights Reserved.
  # 
  # This software is subject to the provisions of the Zope Public License,
  # Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
  # THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
  # WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
  # WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
  # FOR A PARTICULAR PURPOSE
  # 
  ##############################################################################
  """One-line summary goes here.

  Module documentation goes here.

  $Id$
  """

Notes:

  - Doc strings:

    o The first line of the doc string should include a one-line
      description of the module (or class or function).

    o The first line may be followed by additional documentation
      paragraphs, if needed. The additional paragraphs must be separated
      from surrounding text and from each other by blank lines.
    
    o The revision id should come last.

    Here's an example::

      """Implement foo interfaces

      Blah blah

      blah some more

      $Id$
      """

  - Imports

    o All imports should be at the top of the module, after the module
      docstring and/or comments, but before module globals.

      It is sometimes necessary to violate this to address circular
      import pronlems. If this is the case, add a comment to the
      import section at the top of the file to flag that this was done.

    o Ordering

      - Start with imports for standard Python library modules

      - Next come imports from other parts of the Zope library

      - Next come imports from other parts of the current superpackage

      - Last come imports from the current package

      Leave a blank line between each group of imports


<hr>

Some questions and suggestions (Guido):

Should the copyright years be exactly those years where this specific
module is changed?  Or should they always be 2001, 2002?  In a few years,
should we write 2001, 2002, 2003, 2004, 2005, or should we write
2001-2005?

  JimFulton -- I have no idea. Do *you* know the rules for this? If
    so, please add another note.

    I snipped your comments that I think I covered.

Here are my preferences for import order (partly gleaned from
Barry's preferences):

- Use this::

    import os
    import sys

  rather than this::

    import os, sys

  JimFulton -- Gulp. I dunno about this. Do you feel strongly about
    this? Do you think this represents concensus in the Python community?

- Refrain from using relative imports.  Instead of::

    import foo # from same package

  you can write::

    from Zope.App.ThisPackage import foo

  JimFulton -- Why is this a good thing?  This makes moving packages a
    bit harder than it already is.

    I **really** wish Python's import had a mechanism to reference
    modules in containing packages without resorting to full paths.

 


<hr solid id=comments_below>


gvanrossum (May 24, 2002 11:44 am; Comment #2)  --
 On how to write multiple copyright years: someone should ask a lawyer.
 I know the FSF insists that you list each year separately, but I'm
 not sure all lawyers agree with them; I find the long form overly verbose.
 
 Om multiple imports per line: I don't feel strongly about this at all;
 it seems right since the Zope imports are generally so long that you
 do one module per line anyway, so why not do this for the Python modules.
 
 On relative imports: if you move a package, you have to do a global edit
 on all its *users* anyway, so why not include the package itself among
 those users.  I think Tim came up with this rule, after years of experience
 at Dragon.  I believe his reasoning was: a global edit is easy; figuring
 out which imports are relative and which aren't (and what happens when
 there's both a local and a global module with the same name) is hard.
 
klm (May 24, 2002 11:48 am; Comment #3)  --
 <pre>
 > Some questions and suggestions (Guido):
 > - Refrain from using relative imports.  Instead of::
 > 
 >     import foo # from same package
 > 
 >   you can write::
 > 
 >     from Zope.App.ThisPackage import foo
 > 
 >   JimFulton -- Why is this a good thing?  This makes moving packages a
 >     bit harder than it already is.
 > 
 >     I **really** wish Python's import had a mechanism to reference
 >     modules in containing packages without resorting to full paths.
 </pre>
 
 I *really* wish Python's import had a mechanism to explicitly signal relative imports, and supported them in a more thorough way.  Guido, i know you don't accept punctuation shorthand like 'import ..sibling_module' for relative imports, but i think *some* explicit signification would reduce or eliminate the  drawbacks to relative imports.  And face it, the tension has persisted over this issue - legitimately, i would surmise - through the life of package imports.
 
efge (May 24, 2002 11:49 am; Comment #4)  --
 <pre>
 > Should the copyright years be exactly those years where this specific
 > module is changed?  Or should they always be 2001, 2002?  In a few years,
 > should we write 2001, 2002, 2003, 2004, 2005, or should we write
 > 2001-2005?
 </pre>
 
 Apparently (see "here":http://www.loc.gov/copyright/circs/circ03.html )
 only the year of first publication is required. Maybe this is US-specific though.
 
klm (May 24, 2002 11:55 am; Comment #6)  --
 I was writing my last comment while guido committed his.  One piece is actually addressed by what i was trying to say:
 
 <pre>
 > gvanrossum (May 24, 2002 11:44 am; Comment #2)  --
 >  at Dragon.  I believe his reasoning was: a global edit is easy; figuring
 >  out which imports are relative and which aren't (and what happens when
 >  there's both a local and a global module with the same name) is hard.
 </pre>
 
 If relative imports were signalled explicitly, then figuring out which imports are relative and which aren't would *not* be hard.  (Even just an extra leading '.' would make the distinction obvious!)
 
gvanrossum (May 24, 2002 12:02 pm; Comment #7)  --
 Yeah, but following Tim's advice, it would be even better if relative
 imports weren't possible at all.
 
 Java doesn't have them AFAIK.
 
bwarsaw (May 24, 2002 12:04 pm; Comment #8)  --
 On copyright years: the FSF's convention is to spell out all the years, but to only include years in which the file is actually "published" with "existing in cvs" not included in "published".
 
 I.e. Foo.py was created in 2001 and was part of a tarball release in 2001 and 2002.  It should by copyright 2001,2002
 
 Bar.py was created in 2001 but not published in a tarball until 2002.  It should be copyright 2002.
 
bwarsaw (May 24, 2002 12:07 pm; Comment #9)  --
 All imports on a separate line: I strongly prefer them because I find them easier to edit (kill a line is easier than highlight some word -- plus the comma! -- in the middle of a line).  More importantly, a file should contain *only* the imports it needs.  If the thing being imported isn't used anywhere (assuming no import side effects <wink>), then it shouldn't be imported.
 
 -1 on relative imports
 
hathawsh (May 24, 2002 12:53 pm; Comment #10)  --
 I've been experimenting with a convention that clarifies imports for the reader: imports from the standard library come first, imports from other packages second, and imports within the package last.  Each group is separated by a blank line.
 
 OTOH I've seen others do the reverse. :-)
 
 I agree with the assessment that relative imports make it harder to find dependencies using grep, but on the other hand, it's harder to write new code when you are required to use absolute imports.  I usually don't know what I want to call a package until it's nearly finished.  Ken, I'm sure there are other reasons relative imports are helpful; can you think of any?
 
klm (May 24, 2002 1:42 pm; Comment #11)  --
 <pre>
 > hathawsh (May 24, 2002 12:53 pm; Comment #10)  --
 > ![...]
 >  usually don't know what I want to call a package until it's nearly
 >  finished.  Ken, I'm sure there are other reasons relative imports
 >  are helpful; can you think of any?
 </pre>
 
 Well, off the top of my head:
 
 - It certainly shortens import lines when your, eg, package has nesting
   and long names::
 
     from Products.PageTemplates.PageTemplateFile import PageTemplateFile
 
   vs, eg::
 
     import .PageTemplateFile
 
 - It simplifies packaging an application with custom versions of
   standard items::
 
     from .lib import email, mimetypes
 
   That *can* be done using mangling of os.path manipulation - but
   mangling of os.path seems to me to be fatally flawed.  It affects all
   other modules in the python process, including potentially other
   applications with their own libraries.  Pshaw.  What this approach
   begs for, to work, is a package-specific path - which is what the
   relative import is all about.
 
 - Of course, sometimes you want to be able incorporate functionality
   from other packages in yours, without exposing or even using the
   whole application.  With hard-coded full paths, you can't just move
   it, or pieces of it, into your application.
 
 Addressing another message:
 
 <pre>
 > gvanrossum (May 24, 2002 12:02 pm; Comment #7)  --
 >  Yeah, but following Tim's advice, it would be even better if relative
 >  imports weren't possible at all.
 </pre>
 
 I was reading your excerpt as saying relative imports are bad because
 they're hard to recognize, and arguing that's a valid criticism of the
 current implementation that should be fixed - thus mitigating that
 drawback of relative imports.
 
 <pre>
 >  Java doesn't have them AFAIK.
 </pre>
 
 Java is a much more rigid language than python, in general.  It makes
 some sense that (1) it expects to have every package occupy its own
 top-level namespace ("com.sun"), and (2) it seems to inherently have
 more obstacles to mixing things together, what with static typing, no
 mixins, less genericity overall.  Python is quite different in these
 aspects.  I wouldn't assume that rigidity in java's import approach
 applies to python.  (Java takes a quite different approach to
 polymorphism, for example, based on static typing of method
 parameters, which doesn't apply in the context of python classes...)
 
hathawsh (May 24, 2002 2:17 pm; Comment #12)  --
 Let me clarify Java's approach: imports from other packages are all absolute, but imports within a package are *implicit*.  That is to say, every other public class in your package is automatically in your namespace.  Java can do this because it also requires a file to define only one public class, the class name must match the filename, and there is no visible distinction between modules and public classes.
 
 Also, Java makes imports a little clearer since there is no need for the "from" keyword and names don't tend to get duplicated like they do in Python ("from Products.ExternalMethod.ExternalMethod import ExternalMethod")
 
 We don't want Java's limitations, of course.  This is only something to think about.
 
rdmurray (May 24, 2002 2:28 pm; Comment #13)  --
 In a lot of python files I've seen::
 
     __version__ = "$Id$"
 
 and while I've never actually *used* the __version__ variable for anything, it has
 a rather pythonic feel to it that pleases me <grin>.
 
