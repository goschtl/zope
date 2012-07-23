##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Topic views.
"""

from Products.CMFDefault.browser.utils import decode
from Products.CMFDefault.browser.utils import memoize
from Products.CMFDefault.browser.utils import ViewBase
from Products.CMFDefault.browser.widgets.batch import BatchViewBase


class TopicView(BatchViewBase):

    def _get_items(self):
        return self.context.queryCatalog()

    @decode
    def listQueries(self):
        queries = self.context.buildQuery()
        return tuple([ '%s: %s' % q for q in queries.items() ])

    @decode
    def listSubtopicInfos(self):
        subtopics = [ {'title': item.Title() or item.getId(),
                       'url': item.absolute_url()}
                      for item in self.context.contentValues() ]
        return subtopics

    @memoize
    @decode
    def listBatchItems(self):
        batch_obj = self._getBatchObj()

        items = []
        for item in batch_obj:
            items.append({'creators': item.listCreators,
                          'date': item.Date,
                          'description': item.Description,
                          'id': item.getId,
                          'title': item.Title and ('(%s)' % item.Title) or '',
                          'url': '%s/view' % item.getURL()})
        return tuple(items)


# XXX: quick-and-dirty port from oldstyle skin
class TopicCriteriaView(ViewBase):

    def __call__(self, ADD=None, DELETE=None, EDIT=None, acquireCriteria=None,
                 criteria=(), field=None, criterion_type=None,
                 criterion_ids=()):
        if ADD:
            self.context.addCriterion(field=field,
                                      criterion_type=criterion_type)
            self.request.response.redirect(self._getViewURL())
            return ''

        elif DELETE and criterion_ids:
            for cid in criterion_ids:
                self.context.deleteCriterion(cid)
            status = 'Criteria+deleted.'
            self.request.response.redirect(
                '%s?portal_status_message=%s' % (self._getViewURL(), status))
            return ''

        elif EDIT:
            if acquireCriteria != self.context.acquireCriteria:
                self.context.acquireCriteria = bool(acquireCriteria)
            for rec in criteria:
                crit = self.context.getCriterion(rec.id)
                command = {}
                for attr in crit.editableAttributes():
                    tmp = getattr(rec, attr, None)
                    # Due to having multiple radio buttons on the same page
                    # with the same name but belonging to different records,
                    # they needed to be associated with different records with
                    # ids
                    if tmp is None:
                        tmp = getattr(rec, '%s__%s' % (attr, rec.id), None)
                    command[attr] = tmp
                crit.apply(command)
            status = 'Changes+saved.'
            self.request.response.redirect(
                '%s?portal_status_message=%s' % (self._getViewURL(), status))
            return ''

        return self.index()
