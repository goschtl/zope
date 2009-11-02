z3c.recipe.depgraph
===================

This buildout recipe generates dependency graphs for packages.

Options
-------

eggs
  The eggs for which graphs are generated. All dependencies of the eggs are
  automatically included.

exclude
  A list of eggs which should be excluded from the graph processing.

re-exclude
  A list of eggs' regular expressions which should be excluded.

dead-ends
  A list of eggs which dependencies should be excluded.

re-dead-ends
  A list of eggs' regular expressions which dependencies should be excluded.

extras
  A boolean determining if extra requirements should be included. Defaults
  to False.

package-map
  An buildout section containing a mapping of distribution names to package
  names.

variants
  A whitespace separated list of variants of graphs to create. The available
  options are::

    base - The basic full graphs.
    tred - The transitive reduction of the graphs.
    scc - Extracts graphs of strongly connected components.

formats
  A whitespace separated list of output-formats to create. Defaults to svg.
  Please consult the manpages for the dot-command or visit the graphviz-website
  for a full list_. Most commonly used options are::

    svg - Scalable Vector Graphics
    png - Portable Network Graphics
    gif - Graphics Interchange Format


 .. _list: http://www.graphviz.org/cvs/doc/info/output.html
