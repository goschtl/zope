This directory is a sandbox for Zope Corporation projects.  We make projects
available here for the community that we plan to move to the open source 
repository but that we are still working with.  As such, the releases are 
snapshots from ongoing work in the zope.com repositories.

We invite comments on these projects.

Projects in the Sandbox typically require Python >= 2.4.1.

Current contents:

 - catalog: this expects to live in zc.catalog.  It contains the following
   bits:
   
   * an extent catalog.  This is a subclass of the zope.app.catalog that
     has two features.  First, it has a filtered extent.  This allows you to
     control what is added to the catalog as well as a canonical way to query
     the catalog for the entire set of doc ids that it contains.  This comes in
     handy both when you need to intersect the results from another
     catalog-ish search with the contents of this catalog; and when you want to
     perform differences (e.g., give me all of the values in the catalog that
     are not in this index).  Second, and arguably even more interestingly,
     it has a deferred queue for processing indexing and unindexing, so that
     the work all happens at the end of the transaction.  This can be a big win
     if you are performing several operations on each object you touch in a
     transaction: even though a modified event might be fired each time, the
     cataloging work is only done once.

  * a set index.  This is intended to be a more general and more powerful
    version of a keyword index.  The version that would go in zope/index is in
    index.py, and the version that would go in zope/app/catalog (e.g., that you
    would use in a typical Zope 3 application) is in catalogindex.  It has
    some nice features, a couple of which require an extent catalog.

  * a value index.  This is intended to be a replacement for zope 3's field
    index.  It shares the design and more powerful queries of the set index.
    Find the indexes in index.py and catalogindex.py, as above.

  * a normalizer index wrapper.  This lets you write a normalizer, with a
    fairly small API, and then combine it with another basic index for an index
    more tightly coupled with a given data type (and indexes should confine
    themselves to a single data type).  For instance, it could be used to
    build...

  * set and value indexes for datetimes.  The normalizer lets you set
    resolutions so that indexed datetimes are stored only to a given
    resolution, enforces the indexing of timezone-aware datetimes, and lets
    you query using dates, naive datetimes, aware datetimes.  see index.py and
    catalogindex.py, as above.

  * a stemmer for the zope/index/text index based on Andreas Jung's work on
    the TextIndexNG.  TextIndexNG has many admirable advantages.  We couldn't
    use it for our use cases because we required relevance ranking and the
    speed that Tim Peters and other ZC employees had put into the 
    zope/index/text code.  Until TextIndexNG surpasses zope/index/text (and
    Andreas plans to, I believe :-) ) in those areas, we want to at least take
    advantage of some of his code.  The stemmer in zc.catalog is a pipeline
    element for a zope/index/text/lexicon that wraps Andreas' wrapper of
    M.F. Porter's snowball stemming work (http://snowball.tartarus.org/).

  * something that converts the atoms of a text index query to all globs.
    ignore this.  :-)  It was in case we couldn't get the stemming to work
    quickly enough.
  
  The plans for this code will be to move as much of it as possible to 
  zope/index and zope/app/catalog, as appropriate, after 3.1.

- listcontainer: this expects to live in zc.listcontainer.  It is an odd bird--
  a list containing linked list members.  It allows objects to live both within
  a dict-like zope/app/container and the list-like listcontainer,
  simultaneously.  It fires a full set of events, and supports powerful move
  operations, similar to the zope objectmover.  It is useful for modeling
  nameless object hierarchies, particularly (but not only) when the objects
  must also live simultaneously within a zope/app/container named heirarchy.
  Very nice, and well tested, in the specialized uses for which it is designed.

  This will eventually either move to zope.app or its own (public) project.

- mechtest: this expects to live in zc.mechtest.  It provides a browser-like
  interface for doing functional tests.


Upcoming contents: 

a union field, a combination field, and widgets for both.  Not included now
because they need to be separated out from some other old code (superceded by
zope.formlib).

Past contents:

 - page: development on this has moved from the zope.com repositories into
   zope.org.  It may be checked out from its canonical location in 
   svn.zope.org/repos/main/zope.formlib/trunk/ .
   
