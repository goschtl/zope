=============================
Kirbi: a P2P library manager
=============================

Kirbi is a sample application to test Grok and help programmers learn
how to use it to build a complete app.

Kirbi also aims to be useful and not just a sample. It is a system to allow
friends and colleagues to share their books and DVDs without losing track
of them.

Use cases
===========

Done
-----

* Add books to the public catalog via a Web form or XML-RPC

* Allow searches to the public catalog

* Add books by entering just the ISBN, and letting Kirbi fetch the book data
  from Amazon.com

To Do
------

* User self-registration

* User catalogs own collections

* User invites friends to share specific collections

* User requests to borrow an item

* User approves the loan of an item

* User tracks lent items

* User tracks borrowed items
  
* Add books by entering title words or author names, and letting Kirbi fetch
  some likely candidates from Amazon.com

Other tasks
===========

* Refactor kirbifetch to allow pluggable metadata sources, instead of
  relying on Amazon.com exclusively

* Increase test coverage

* Packaging (buildout, eggification)

* AJAXification using same framework used for Grok Admin UI


