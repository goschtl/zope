# -*- coding: UTF-8 -*-

"""OCQL interfaces

$Id$
"""

from zope.interface import Interface
from zope.interface import Attribute

################
# Components
################

class IEngine(Interface):
    def compile(query):
        """
        """

class IQueryParser(Interface):
    """Parse the query string and build a query object tree representing
    the query.
    """

class IQueryOptimizer(Interface):
    """Makes some simplifications on the query object tree. Input/output
    is the same format: query object tree.
    """

class IRewriter(Interface):
    """Rewrites the query object tree to Collection Algebra.
    Output is an Algebra object.
    """

class IAlgebraOptimizer(Interface):
    """Optimizes the query using the Collection Algebra identity operations.
    This component contains only the code of the optimizer logic.
    Input/output is the same format: Algebra object.
    """

class IAlgebraCompiler(Interface):
    """ Compiles the algebra object into python lambda and list comprehension.
    Output is an object that holds all information necessary to run the query.
    Embeds the relation and index retrieval component information in the compiled object.
    """

class IDB(Interface):
    """DB metadata and data provider
    Provides database metadata to the engine.
    - class/object declarations (from interface declarations)
    - index information (from zope catalogs and indexes)
    - relationship information ()
    Provides data extraction support for
    - index values/objects
    - relation/related objects
    """

################
# Objects passed around
################

class IObjectQuery(Interface):
    """Objects providing this interface represent the OCQL query
    as python objects
    """

class IOptimizedObjectQuery(Interface):
    """Objects providing this interface represent the OCQL query
    as python objects
    """

class IAlgebraObject(Interface):
    """Objects providing this interface represent the
    rewritten ObjectQuery to Algebra objects
    """

class IOptimizedAlgebraObject(Interface):
    """Objects providing this interface represent the
    rewritten ObjectQuery to Algebra objects
    """

class IRunnableQuery(Interface):
    """Objects providing this interface represent the
    runnable query
    """

    def execute():
        """Run the query, return the resulting dataset
        """

    def reanalyze():
        """Reanalyze and reoptimize the query according to the current
        contents of the database
        """

################
#
################

class ILogger(Interface):
    """ Everything must be logged!
    I want to be able to hunt for bugs and bottlenecks.
        - component inputs
        - component outputs
        - component runtimes
    All components shall log here.
    """

class IStatistics(Interface):
    """Stores statistical data based on queries run before.
    Provides statistical data for optimization.
    """
