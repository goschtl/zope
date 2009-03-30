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
