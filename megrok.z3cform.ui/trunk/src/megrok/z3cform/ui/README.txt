=================
megrok.z3cform.ui
=================

This package is a wrapper/helper around megrok.z3cform.base and
z3c.formui. This means if you use megrok.z3cform.base and you want
benefit form the already existent default forms form z3c.formui,
just add megrok.z3cform.ui to your install_requires in your setup.py
and you are fine.

In general megrok.z3cform.ui does nothing more then installing
z3c.formui. And it marks the default with the IDivFormLayer interface
from z3c.formui. So you will get your form in a nice div-based
layout.
