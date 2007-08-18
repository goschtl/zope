=====================
TransactionalMailHost
=====================


What is TransactionMailHost
===========================

TransactionalMailHost is yet another MailHost implementation.
It integrates with the transaction system of Zope in order
to send out email  only in case of a committed transaction.


Requirements
============

- Zope 2.9+
- zope.sendmail


Installation
============

- Unpack the archive in your *Products* directory
- restart Zope
- create a new **TransactionMailHost** instance through the ZMI

Note
====

TransactionMailHost is not (yet) an API compatible with the 
Zope MailHost implementation. It provides only one public method
right now:

   send(fromaddr, toaddrs, message)


Author
======

TransactionalMailHost was written by Andreas Jung 
for ZOPYX Ltd. & Co. KG, Tuebingen, Germany.


License
=======

TransactionalMailHost is licensed under the Zope Public License 2.1. 

See LICENSE.txt.


Contact
=======

| ZOPYX Ltd. & Co. KG
| Andreas Jung
| Charlottenstr. 37/1
| D-72070 Tuebingen, Germany 
| E-mail: info at zopyx dot com
| Web: http://www.zopyx.com


Credits
=======

Parts of the code are influenced by z3c.zalchemy (Juergen Kartnaller, Michael
Bernstein & others) and Alchemist/ore.alchemist (Kapil Thangavelu). Thanks to
Martin Aspeli for giving valuable feedback.

