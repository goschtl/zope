##############################################################################
#
# Copyright (c) 2006-2007 Lovely Systems and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id$
"""
__docformat__ = "reStructuredText"

from zope.formlib import form

from interfaces import IRepair


class Repair(form.Form):

    form_fields = form.FormFields()

    def repairable(self, *args):
        try:
            IRepair(self.context)
        except TypeError:
            return False
        return True

    def notRepairable(self, *args):
        return not self.repairable()

    @form.action(u'Repair', condition='repairable')
    def do_repair(self, action, data):
        repairer = IRepair(self.context)
        count = repairer.repair()
        self.status = u'Repaired %s relations' %count

    @form.action(u'Not Repairable', condition='notRepairable')
    def do_notrepair(self, action, data):
        self.status = u"I said I'm not repairable !"

