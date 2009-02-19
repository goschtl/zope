Defining Interfaces
===================

  Status: IsDraft

  1. All public interfaces should go into a file called 'interfaces.py'. 
     By "public" I mean interfaces that you expect to be implemented more
     than once. Interfaces that are likely to be implemented only once,
     like 'IGlobalAdapterService', should live in the same module as their
     implementation.

  2. The interface name should always start with an "I", for example 
     "ITranslationDomain".

  3. One function of interfaces is to document functionality, so be very 
     verbose with the documentation strings.

  4. You should always derive from the Interface "class" somewhere in your inheritance 
     tree.


  Example::

    from Interface import Interface

    class IDublinCoreTitle(Interface):
         """This interface will provide a title handler for common 
            content objects.
         """

         def getTitle():
             """Get the title from the object."""
 
         def setTitle(title):
             """Set the title of the object."""
     

Using Interfaces

  1. Declare that a class or module implements an interface by 
     using 'zope.interface.implements'::

       from zope.interface import Interface, implements

       class IFoo(Interface):
            pass

       class Foo(object):
            implements(IFoo)

  2. To directly declare that an object provides an interface, use 
     'zope.interface.directlyProvides' or 'zope.interface.alsoProvides'::

       from zope.interface import Interface, directlyProvides

       class IFoo(Interface):
            pass

       class Foo(object):
            pass

       foo = Foo()
       directlyProvides(foo, IFoo)

     But be careful, 'direclyProvides()' can only be used once and does not 
     accumulate provided interfaces.   'alsoProvides()' is often preferable
     since it strictly augments the set of provided interfaces.


<hr solid id=comments_below>


hathawsh (Jan 26, 2002 10:15 pm; Comment #1)  --
 I try to use a convention for interface documentation that I first noticed in Java interfaces.  I write in the present tense rather than the imperative tense.
 
 An example of imperative tense: "Write the message to stdout and return".
 
 An example of present tense: "Writes the message to stdout and returns".
 
 The distinction seems very subtle at first.  But the distinction is meaningful and, at least for me, quite helpful.  When I saw this pattern in the documentation for the Java standard library and started applying it, I chipped away a lot of my "interface writer's block" and finally knew what to write.
 
 When you write in the imperative tense you are effectively giving instructions to the computer.  Choose the imperative tense when you are describing what a block of code is supposed to do in a more human-readable form.
 
 But interfaces specify a contract, not an implementation.  So the interface documentation should describe what each method does, not how.  The present tense encourages you to do this.
 
 One minor drawback is that you end up with incomplete sentences since you usually drop off the subject.  But don't prepend "This method..." or "This class..." to all of your interface documentation strings since that is just redundant.  Incomplete sentences are appropriate in certain contexts.
 
 So I would change the example above to read::
 
   class IDublinCoreTitle(Interface):
        """Provides access to the Dublin Core title property.
        """
 
        def getTitle():
            """Gets the title from the object."""
  
        def setTitle(title):
            """Sets the title of the object."""
 
 
 Note that converting to present tense uncovered a minor problem with the interface: there is no reason (currently) that the interface can only be applied to "common content objects", so I took that part out.  That docstring was actually in the future tense, which unconsciously puts you in the mindset of planning for the future.
 
 This is only a suggestion based on my own experience.  Your choice of tense and person (1st, 2nd, or 3rd person) has unconscious effects on you as a writer.  If you choose the right tense and person, you're more likely to communicate effectively.
 
 
fdrake (May 24, 2002 10:08 am; Comment #2)  --
 I definately agree with Shane on this one.  Much of the older content in the Python documentation was written in the imperative style because that's what Guido likes (or did at the time, at least), and it always feels very tedious to read.
 
 The imperative style is properly used when telling the **reader** to do something, not when describing what something else will do.  It makes a lot more sense to use present tense to describe an interface and the imperative to tell the user they must do something.
 
gvanrossum (May 24, 2002 12:49 pm; Comment #3)  --
 I've always liked the imperative style better, but I will see if I can
 get used to the present tense.
 
Caseman (May 24, 2002 2:53 pm; Comment #4)  --
 Funny, I always used to write comments in present tense, but after seeing a bunch of code commented
 in imperial tense, I've changed. Although, I still find myself going back to present tense every once
 in a while.
 
 I would argue that either is OK, so long as the whole module uses one or the other. It reads really strange
 to me when some comments are in imperial tense and others are in present tense.
 
rdmurray (Aug 30, 2002 4:12 pm; Comment #5)  --
 <pre>
 > fdrake (May 24, 2002 10:08 am; Comment #2)  --
 >  The imperative style is properly used when telling the **reader** to do
 >    something, not when describing what something else will do.  It makes a
 >    lot more sense to use present tense to describe an interface and the
 >    imperative to tell the user they must do something.
 </pre>
 
 I've always used imperitive tense, because I figured I *was*
 telling the reader what to do: what they needed to code their method
 to do if they were going to implement this particular interface.
 I can see it both ways.  But I can see that I can equally think of the
 Interface as documentation of what the implemented methods do, which
 is surely the more common reader case.
 


From zagy Wed Feb 18 05:12:35 -0500 2009
From: zagy
Date: Wed, 18 Feb 2009 05:12:35 -0500
Subject: 
Message-ID: <20090218051235-0500@wiki.zope.org>

I see more and more transition to pep8 in regard to method names, like get_title() instead of getTitle(). Shouldn't we update guides accordingly?
