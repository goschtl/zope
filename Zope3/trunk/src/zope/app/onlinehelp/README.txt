Online Help System

  What's the Online Help System?

    Stephan Richter has implemented a very basic Online Help that supports
    plain text and HTML files for content in help topics. Topics are a piece
    of the help document that contains useful information. Topics are also
    containers and can simply contain further Topics. This way we can have
    nested help pages, which will help with content organization. It is
    possible to associate a topic with a particular view of an interface.
    The online help system is implemented as global service.


  Usage:

    To register help topic for your code, you need to add 'register'
    directive in the configuration file (see example below). You can
    specify the following attributes:

      parent   - Location of this topic's parent in the OnlineHelp tree.
                 Optional.
      id       - The id of the help topic. Required.
      title    - The title of the topic. It will be used in the tree as
                 Identification. Required.
      doc_path - Path to the file that contains the topic. Required.
      doc_type - Defines the type of document this topic will be. Optional.
      for      - The interface this topic apllies to. Optional.
      view     - The name of the view for wich this topic is registred.
                 Optional.

    To unregister a particular help topic use directive unregister. You need
    to specify the path to the help topic.


  Examples:

    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:help="http://namespaces.zope.org/help"
        >

    ....

    <!-- Register initial Help Topics -->

    <help:register
        id = "ui"
        title = "Zope UI Help"
        doc_path = "./ui.txt" />

    <help:register 
        id = "welcome"
        title = "Welcome"
        parent = "ui"
        for = "zope.app.interfaces.onlinehelp.IOnlineHelpTopic"
        view = "zope.app.browser.onlinehelp.OnlineHelpTopicView"
        doc_path = "./help.txt" />

    </configure>
