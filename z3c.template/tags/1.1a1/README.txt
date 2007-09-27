=============
Z3C Templates
=============

This package allows us to separate the registration of the view code and the
layout.

A template is used for separate the HTML part from a view. This is done in
z3 via a page templates. Such page template are implemented in the view,
registered included in a page directive etc. But they do not use the adapter
pattern which makes it hard to replace existing templates.

Another part of template is, that they normaly separate one part presenting
content from a view and another part offer a layout used by the content
template.
