Bug Tracker Product for Zope 3
==============================

  This product is an implementation of a bug tracker in Zope 3. 

  Features
  --------

    Bug Tracker

      - View list of bugs

        o Filtering by status, type, release, priority and text

        o Batching, when list of bugs becomes too long.

        o Bug status and priority values are marked up based on value.

      - Settings

        o When creating a Bug Tracker, one can select the option to
          automatically create a set of status, type, release and priority
          choices.

        o The choices for the status, type, release and priority are flexible
          and can be changed.

      - Mail Subscriptions

        o These are Bug Tracker wide mail subscriptions that send the
          recipients an E-mail about additions, changes and deletions of bugs.

    Bug

      - Overview

        o This screen provides a comprehensive overview of all the available
          information about the bug.

        o The status and priority are marked up based on their value.

        o The description and the comments are rendered using STX.

        o Upload Files and Images

        o Add new comments

      - Edit

        o To provide a familiar interface, the edit form is layed out in the
          same way as the overview

      - Dependencies

        o In my opinion, one major improvement over the current collector is
          the availability of a dependency feature, where I can say that this
          bug depends on that one.

        o Based on this information a dependency tree is generated using the 
          markup rules for status and priority, so that a user can quickly 
          recognize critical spots in the tree.

        o There is also a Statistics section that tells you how many bugs are
          completed, have not been viewed and are being fixed. 

      - Mail Subscriptions

        o These are specific bug mail subscriptions that send the recipients
          an E-mail about additions, changes and deletions of the bug.
