Welcome to Zope source release
-------------------------------------

  This document provides some general information about the Zope
  source release and provides links to other documents.

  Installation information can be found in doc/INSTALL.txt.

  Zope information is available at http://www.zope.org/

  Report problems with this release on the Zope mailing list
  (zope@zope.org) To subscribe to the list send mail to
  zope-request@zope.org with "subscribe" in the subject line.

Introduction:

  The source release is intended for tinkerers, those who want
  to use Zope components separately, Bobo hackers, people who
  want to use  their own Python, and people who work on obscure
  platforms because they love to compile everything from source.

  If you just want to use Zope easily and aren't a programmer
  the binary release will probably suit you better.

License

  A preliminary version of the Zope License is included in LICENSE.txt
  We are still working on finalizing the license. Send your feeback about
  the license to zope-license@zope.org. 

Installing Zope:

  Follow the instructions in doc/INSTALL.txt to install Zope. You
  may wish to run the installer even if you only plan on using
  selected Zope components since the install script compiles
  Python extensions for you that you may want, like cDocumentTemplate.

Using Zope Components Separately

  Zope consists of many Python packages which can be profitably
  used by themselves. For example you will find all your old friends
  from Bobo here:

    * ZPublisher - A packagized version of the Bobo ORB you know and
      love. It's been updated with new thinks like support for
      __bobo_debug_mode__

    * DocumentTemplate - This package includes cDocumentTemplate which
      speeds things up considerably.

    * BoboPOS - This is NOT BoboPOS3. It a version of BoboPOS2 which
      include c code to make things faster.

  You can find most of these packages in the lib/python directory. If
  you poke around, you might find other goodies too, like StructuredText.

  ZPublisher and DocumentTemplate are also available separately.

Notes

  * Zope requires Python 1.5.1
  * Lots more documentation is coming.
  * Don't forget to check the Zope web site and mailing list.
  * Read the source, have fun!

