.. role:: header
.. role:: zsection

.. container::
   :class: menuacross

   + `What is Zope? <index.html>`_
   + `Who is Zope? <who_is_zope.html>`_
   + `Why Zope? <why_use_zope.html>`_

.. container::
   :class: LeftCol

   .. rubric:: Zope is a Community

   Hundreds of companies and thousands of developers devoted to solutions to
   the perennial problems of building complex, scalable web applications.
   `More... <who_is_zope.rst>`__

   .. rubric:: Zope is Open Source

   All Zope libraries, frameworks, and applications managed by the `Zope
   Foundation`_ are licensed under the OSS-Certified `Zope Public License`_.
   This BSD-style license allows use in both open source projects and closed
   proprietary product offerings.

   .. rubric:: Zope is a Broad Software Technology

   The base Zope Framework has powered web development frameworks, web
   application servers, content management systems, and many other software
   components.

   .. rubric:: Zope is Mature

   Zope's robust technologies are born of 10 years of hard-won real world
   experience in building production web applications for every level
   of organization, ranging from small nonprofits to large enterprise systems
   and high traffic public web applications. `More... <why_use_zope.rst>`__

   .. rubric:: Zope is Python-based

   Zope is written in `Python`_, a highly-productive, object-oriented
   scripting language.


.. container::
   :class: RightCol

   .. container::
      :class: frameworks

      :zsection:`Frameworks`

      The following are notable frameworks which users are advised to look at if
      they are looking at entering the world of Zope.

      .. container::
         :class: framework

         |Grok|_

         aimed at making the full power of the Zope Framework accessible to any
         Python developer.

      .. container::
         :class: framework

         |Repoze|_

         a web framework toolkit integrating WSGI middleware with Zope.

      .. container::
         :class: framework

         |Zope 2|_

         a mature application server which has thrived in enterprise production
         systems for nearly 10 years.


   .. container::
      :class: applications

      :zsection:`Applications`

      Several applications are built atop the Zope Framework, providing rich user
      experiences.

      .. container::
         :class: application

         |Plone|_

         a powerful, flexible Content Management solution that is easy to
         install, use and extend.

      .. container::
         :class: application

         |Schooltool|_

         a project to develop a common global school administration
         infrastructure that is freely available under an Open Source license.

      .. container::
         :class: application

         |Launchpad|_

         both an application and a web site supporting software development,
         particularly that of free software.  Launchpad is developed and
         maintained by Canonical Ltd.


   .. container::
      :class: composeyourown

      :zsection:`Compose Your Own`

      To compose your own application or framework from scratch, or see how the
      packages within the Zope Framework can work for you, see more information
      below.

      * `Zope 2 Application Server`_, a mature application server which has
        thrived in enterprise production systems for nearly 10 years.

      * `Zope Framework Wiki`_, a place where more information about the Zope
         framework can be found.

      This variety of open source and commercial applications built from Zope
      Framework demonstrates a community with years of expertise solving a wide
      range of problems. A deeper inspection of the technology reveals powerful
      tools for managing complexity by fully leveraging the best dynamic features
      of the Python programming language.

.. raw:: html

   <br clear="all" />


Python Community Cross-Pollination
===================================

Zope software components are also deployed in the wider Python community; for
example:

* `Twisted`_, an asynchronous network server written in Python
  utilizes *zope.interface*. Some Zope projects come bundled with
  Twisted to provide Zope with a powerful multi-protocol network layer.

* `TurboGears`_, a Python web framework which utilizes zope.interface
  as well as Zope's transaction library.

* `buildout`_, originally developed at Zope Corporation, has gained traction outside the
  Zope Community as a Python-based build system for creating, assembling and
  deploying applications from multiple components.

.. |Grok| image:: _static/grok_logo.png
.. _`Grok`: http://grok.zope.org

.. |Repoze| image:: _static/repoze_logo.gif
.. _`Repoze`: http://static.repoze.org/bfgdocs/

.. |Zope 2| image:: _static/zope2_logo.png
.. _`Zope 2`: http://zope2.zopyx.de/

.. |Plone| image:: _static/plone_logo.png
.. _`Plone`: http://plone.org

.. |Schooltool| image:: _static/schooltool_logo.png
.. _`Schooltool`: http://www.schooltool.org/

.. |Launchpad| image:: _static/launchpad_logo.png
.. _`Launchpad`:  http://launchpad.net


.. _`Zope 2 Application Server`: http://zope2.zopyx.de/
.. _`Zope Framework Wiki`: http://wiki.zope.org/zope3/Zope3Wiki/
.. _`BFG`: http://static.repoze.org/bfgdocs/
.. _`Twisted`: http://twistedmatrix.com/trac/
.. _`Zope Foundation`: http://foundation.zope.org/about
.. _`Turbogears`: http://turbogears.org/
.. _`buildout`: http://buildout.org
.. _`Zope Public License`: http://www.zope.org/Resources/License/
.. _`Python`: http://www.python.org/
