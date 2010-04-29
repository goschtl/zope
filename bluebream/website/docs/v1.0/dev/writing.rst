Guidelines for writing documentation 
====================================

Original location: http://www.zope.org/DocProjects/writing_tips

Overview
--------

Clear writing is hard.  Explaining a complex subject like computer
software to a novice audience is difficult because you, the writer,
are immersed in technical details before you even begin writing.

Your task is to bring the reader to a level of familiarity with
your subject equal to, or at least close to, your own familiarity.
Writing in an unclear way, or drowning the reader in technical
details will confuse them, cause them to "skim" the material, and
come away with bad or false impressions of you or your subject.

This guide gives you practical advice, from my own writing
experience, to help you develop clear, instructive, maintainable, and
ultimately *valuable* software documentation.  What follows is a
series of rules that you can apply to what you've written, or are
going to write, to improve the documentation you produce.

These tips do not attempt to cover the most common English usage and
composition errors.  I consider the best resource of usage and
composition rules to be `The Elements of Style
<http://www.bartleby.com/141/>`_ by William Strunk, Jr.  A follow up
of this book, edited and expanded by E. B.  White, is also available
(and is the most common edition found in bookstores).  *The Elements
of Style* is indispensable for anyone whose task is to write clear
English.  While the rules presented here are inspired by, and often
reiterate, rules and concepts from *The Elements of Style*, their
focus is primarily toward writing clear documentation for computer
software, or anything equivalently technical.

Here are some interesting links on the web to other style-related
documents and references:


- `English usage in Cyberspace <http://www.dsiegel.com/tips/wonk9/usage.html>`_
- `Writer's General Reference <http://alabanza.com/kabacoff/Inter-Links/>`_


Writing Tips
------------

Speak directly to the reader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Address the reader in the second person as "you" , and use the
possessive "your".

Use first person sparingly and only to refer to yourself: the writer.
"We" should not be used to *include* yourself with the reader, but
only to refer to multiple authors.  Here is an example of text that
includes the author with the reader:

    When we add a new method to this class, it will override any
    methods with the same name defined in our subclasses.

This is often referred to as "The Royal We".  Fixing this is almost
always a simple transformation:

    When you add a new method to this class, it will override any
    methods with the same name defined in your subclasses.

Be assertive
~~~~~~~~~~~~

Do not speak in a weak, indefinite, or probable way.

As described in *The Elements of Style* (rule #11), use the active
voice.  This is so common an error it is worth repeating here with
some examples.  Active voice means engaging the subject of a sentence
with an active verb.  The opposite, passive voice, usually involves
saying that the subject constantly *is* doing some infinitive action.
For example:

    Something to remember about ``ZPublisher`` is that it will refuse
    to publish any method that doesn't have a doc string.

    The standard convention for product management is to provide a
    series of tabbed management screens.

Here are the same sentences speaking in active voice.  Notice how
this sometimes involves rearranging the sentence:

    Remember, ``ZPublisher`` refuses to publish any method that lacks a
    doc string.

    Tabbed management screens provide a standard convention for product
    management.

Do not speak in probable terms like may, maybe, or probably.  This is
often the unconscious effect of writing documentation before the
software it describes is written.  Be assertive, and state what is,
not what may be.  "Maybe" can be struck entirely.  "May be" and
"probably is" can be replaced by "is".  "Should" sometimes falls
under this rule also.

Explain key ideas in simple terms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Documentation should explain key ideas to the reader.  Often, these
ideas are not obvious to the reader when they use the software, and
therefore must be explained.

Writers are tempted to explain key ideas in terms of concrete
technical details those ideas are based on.  Unless your are
specificly targeting an audience that seeks technical details,
readers are often uninterested (at least initially) in the details
that implement a key idea.  Would you describe a building to a
cave-dweller as a shelter from the elements, or a collection of
bricks, boards, nails and other materials? Would you describe a car
as an object that transports you from one place to another, or as a
machine with pistons, brakes, wires and other parts? The first of
these descriptions are the key ideas, the second of them are the
details that implement the key ideas.  If your audience seeks
implementation details and is already familiar with the key idea then
detailed explanation is correct.  If you audience is the equivalent
of a cave-dweller to your subject, then you must avoid implementation
and focus on the key idea at first.

When a reader fails to understand the meaning of documentation, it is
usually because they encounter a word they do not understand.  Clear
explanation involves building a key idea in the readers mind using a
succession of simple terms *they can understand*.  When you throw an
implementation detail in the explanation before they key idea is
completed the reader stumbles; resulting in confusion.  The reader
skims over the technical parts that they don't understand yet, or
can't understand yet, because you have not completed explaining the
key idea to them.  For example, the first paragraph of a draft of
user documentation for Zope's Python Methods states:

    All of Zope's capabilities are provided by methods, one way or
    another.  When you ask Zope for a URL, it first fetches an object
    from the ZODB and then calls some method of that object.  The
    methods of built-in Zope objects are defined in Zope's source
    code, or in Python classes stored in Product modules on the
    filesystem.  Additional object classes (and their methods) can be
    defined by creating new filesystem Products, and this is
    appropriate when the implementation of a class requires extensive
    access to resources (such as the filesystem) which should be
    carefully protected.

Before readers can even begin to understand what this paragraph is
really saying they must understand ZODB, methods on objects, built-in
Zope objects, what or where Zope's source code is, Python classes,
Product modules, the file-system, object classes (and their methods),
file-system Products, and why implementing them involves a class if
it requires extensive access to resources which should be carefully
protected.  The first sentence should really say something like:

    You can write simple scripts in Zope in the Python programming
    language with Python Methods.

Students in Driver's Education do not learn how to use a steering
wheel by being told about rack-and-pinions, Cardon shafts, toe,
castor or double-wishbone suspensions.  None of these technical
details are relevant to teaching a driver's-ed student to steer a
car.

Use simple examples
~~~~~~~~~~~~~~~~~~~

Prose documentation is used to explain a key idea to the reader.  An
example is used to show a key idea to the reader.  Both methods are
very complimentary; prose documentation explains the workings of an
example, and an example reveals the concrete concept behind an
explanation.

Your explanations should not be overly complex and neither should
your examples.  The level of complexity that is appropriate for both
your explanations and your examples depends on your target audience,
but neither should be written to *exceed* the level of complexity
your target audience is expected to understand.

Avoid colloquial expression
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Speak simply.  If your audience is global, you cannot assume your
reader's native language is English.  Colloquial speech is
unnecessary and distracting for a reader that struggles to understand
not only the concept your are describing, but also the language you
are describing it in.

    By adjusting the interpreter *check interval* to reduce how often
    Python switches contexts you can really make Zope scream.

Should be written as:

    By adjusting the interpreter *check interval* to reduce how often
    Python switches contexts you can really improve performance.

Provide answers, not questions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is tempting to ask a question followed immediately by the answer.
For example:

    What if you want the reptile page to display something besides the
    welcome message? You can replace the \*index\_html\* method in the
    reptile section with a more appropriate display method, and still
    take advantage of the zoo header and footer including navigation.

The question serves only to introduce a concept, not really to ask a
question of the reader.  State the concept directly:

    To display something besides the welcome message on the reptile
    page, replace the \*index\_html\* method in the reptile section
    with a more appropriate display method.  This still takes
    advantage of the zoo header and footer, including navigation.

The result is a more assertive paragraph, one less sentence, and
fewer words.

This does not mean you should never ask questions, rather, you
should ask questions to make the reader think about a possibility,
or to engage their imagination, not to introduce a concept that can
be stated directly.

Revise sentences that say little or nothing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following sentences say little or nothing, and should be struck.
What concepts they do present should be revised into surrounding
sentences:

    At first it would appear straightforward.

    You should begin at the beginning.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
