One of the design goals of Zope is to allow designers to check in HTML
template, CSS and Javascript files, which just work (with some additional
information). For HTML code we use Zope's Page Templates to accomplish this
objective. For CSS and Javascript we did not need such a feature until now,
since those files were largely static or variables could be inserted using
other ways at runtime.

However, in CSS URLs -- for example for background images -- are now
frequently inserted into CSS directives. However, the path layout for the
designer might not equal the resource file structure. This package provides a
simple mechanism to replace strings by another.

To accomplish this, a templated resource is provided. The template syntax is
provided in a way that it does not interfere with the syntax of the
resource. For both, Javascript and CSS, this is a comment of the form ``/*
... */``.

Here is the general syntax::

  <COMMAND-BEGIN> <ZRT-COMMAND>: <COMMAND-ARGUMENTS> <COMMAND-END>

Here is an example for CSS:

  /* zrt-replace: ".." "@@" */

