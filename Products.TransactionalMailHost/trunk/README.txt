=====================
TransactionalMailHost
=====================


What is TransactionMailHost
===========================

TransactionalMailHost is yet another MailHost implementation.  It integrates
with the transaction system of Zope in order to send out email  only in case of
a committed transaction. TMH currently supports standard SMTP and SMTP AUTH.


Requirements
============

- Zope 2.9+
- zope.sendmail


Installation
============

- Unpack the archive in your *Products* directory
- restart Zope
- create a new **TransactionMailHost** instance through the ZMI
- configure your SMTP host, port within the ZMI.
  username and password are optional for SMTP AUTH


Note
====

TransactionMailHost is not fully (yet) API compatible with the Zope MailHost
implementation. It provides only one public method right now:

   send(message, fromaddr, toaddrs, subject, encode)

   The 'subject' and 'encode' parameters are unused right now


How does it compare to MailDropHost
===================================

MDH decouples the process of sending mail from its delivery.  Like all other
MailHost implementations TransactionalMailHost blocks the current Zope thread
until the end of delivery. This can be a big disadvantage when you send out
email to multiple addresses. If you run a site producing lots of email you
might better checkout MailDropHost. 


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


