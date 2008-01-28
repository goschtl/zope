
=======================
The Grok IMDB interface
=======================

The Grok IMDB provides a little database to store information about
movies. You can create an instance of the grokimdb as follows::

   >>> from grokimdb.app import GrokIMDB
   >>> mydb = GrokIMDB()
   >>> mydb
   <grokimdb.app.GrokIMDB object at 0x...>

Now we have a GrokIMDB object.

At first, the database is empty::

   >>> list(mydb)
   []

We can add movies to the database::

   >>> from grokimdb.app import Movie
   >>> mymovie = Movie()
   >>> mydb['entry1'] = mymovie
   >>> list(mydb)
   [u'entry1']

We can obtain entries from the database::

   >>> mydb['entry1']
   <grokimdb.app.Movie object at 0x...>

We cannot replace entries once they are in::

   >>> mydb['entry1'] = Movie()
   Traceback (most recent call last):
   ...
   DuplicationError: entry1

We can remove existing entries:

   >>> del mydb['entry1']
   >>> list(mydb)
   []

Now the database is empty as it was in the beginning.

