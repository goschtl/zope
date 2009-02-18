Naming convention Python objects in Zope

  by JimFulton

  I've resisted establishing naming conventions, but enough people
  have asked that conventions be established (and that I follow them ;)
  that I've decided to write down some. So, here they are:

  1. Use leading underscores as described in the "Python Style Guide",
     http://www.python.org/peps/pep-0008.html

  2. Public global variables names are spelled with CapitalizedWords, 
     as in 'Folder' or 'RoleService'.

     Interface names always start with a capital 'I', followed by a
     capital letter, as in 'IFactory'.

     An exception is made for global non-factory functions, which are
     typically spelled with [mixedCase].

  3. Public attribute names are [mixedCase], as in "getService" or 'register'.

  4. Local variables, including argument names
     LowercaseWithUnderscores, as in 'permission_id', or 'service'.

  5. Single-letter variable names should be avoided unless:

     - Their meaning is extremly obvious from the context, and

     - Brevity is desireable

     The most obviouse case for single-letter variables is for
     iteration variables.

  Be tolerant of code that doesn't follow these conventions. We want
  to reuse lots of software written for other projects, which may not
  follow these conventions.

  A reasonable goal is that code covered by the ZPL should follow
  these conventions.

