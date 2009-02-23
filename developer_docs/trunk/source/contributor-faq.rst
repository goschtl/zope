Contributor FAQ
---------------


Zope Corporation (ZC) is opening the Zope Subversion repository to allow checkins
from external contributors.  This document provides answers to
frequently asked questions about the Zope Subversion approach and policies
for contributors.

How do I become a contributor?

    Contributors generally start out by first participating in discussions
    and contributing patches, becoming known in the community.  Start by
    first playing with Zope via ReadOnlyAccess and joining the 
    `Zope developers mailing list <http://lists.zope.org/mailman/listinfo/zope3-dev>`_.
    Once you get oriented, and realize you want to and can contribute via Subversion,
    ask on the Zope3-dev list or to one of the existing contributors about
    getting commit access.  If the developers see a fit they will invite you
    to join.  (See ContributorIntroduction for more background.)

    Once invited, please fill out the `Zope Contributor Agreement
    <Contributor.pdf>`_ and mail the signed copy to the address on the form.  ZC
    will then create a Subversion login for you, add you to the committers mailing
    list, and send you instructions for setting up your commit access.  Note that
    your authenticated Subversion commits are considered ongoing legal acceptance
    of the terms for contribution.

Why do you require a real signature?

    Good question.  The Python community does not require this, but
    the Mozilla community does.  We're choosing the latter example as
    closer to the goals for commercial legal integrity of Zope.
    Issues of legal status and indemnity are important to ZC and to
    business interests in the Zope community.

What is the joint ownership model?

    When a group of people work together on a software project, the
    resulting material is available under some kind of terms.  In some
    cases, the code is just available with no statement of ownership
    status.

    For many open source projects, the contributor *licenses* their
    contribution to the project but retains the ownership.  Examples
    include Apache, Mozilla, and Python.  In a few open source
    projects, however, there is some organizing legal entity like a
    corporation and contributors assign their intellectual property to
    this entity.  Sun takes this approach, so we're told, on
    OpenOffice.

    These different approaches have problems, either legal or
    political.  Hadar Pedhazur at ZC thought up a new approach that
    draws from a sound background of case law.  Namely, the
    contributor and ZC will have joint ownership of the contibutions.
    Importantly, ZC will always ensure the contribution will be
    available under the open source ZPL license.

What if Zope Corporation gets bought by a Mean Company and takes all the work closed source?

    Essentially, nothing more than would happen now.  ZC can't change
    the rules on currently-released software.  So the horse is out of
    the barn and can't be put back in.  Also, the Mean Corporation is
    just as able to make a closed source product under the previous
    model as they would under this new model.  Of course, in any model
    (except GPL), future contributions can be released under any
    terms.

Can I provide my contributions under a different license, as stated in the License section of the Zope Contributor Agreement?

    In summary, yes but no.  You don't pick the license that you use
    when you give it to us.  Rather, we pick the license to give it to
    others (for our 1/2), and that license is the ZPL.  You, however,
    can pick any license in the world to give the code to anyone other
    than us.

    This language about a different acceptible license is there in
    case we decide at some point to change from the ZPL to a different
    open source license.

Does someone have to jump through all these legal hoops just to submit a small patch?

    The contributor agreement certainly is a heavy process for someone
    that wants to make a small contribution, such as a patch.  These
    contributions are just as important to the health of an open
    source project as major code work.  Thus, Zope should encourage
    patch contributions, not create an enormous disincentive.  At the
    same time, integrity of the code base needs to be maintained.

    For small contributions, simply supply them through a
    communications channel such as the bug tracker or the mailing
    lists.  Alternatively, contact a committer or ZC directly.  A
    committer will then review the patch and assume the legal issues
    of committing it themselves.  Likely they will contact the patch
    submitter and get a confirmation that the patch can be used.

    The committers will have some guidelines on recognizing when it is
    reasonable to accept a patch.  It should be clear when something
    has little basis for being deemed intellectual property, versus a
    major change with advanced algorithms.


