import zope.component

from megrok.rdb.components import Model, Container
from megrok.rdb.schema import Fields
from megrok.rdb.db import Database

from megrok.rdb.directive import key

import collective.lead.interfaces


def query(class_):
    database = zope.component.getUtility(
        collective.lead.interfaces.IDatabase, name='megrok.rdb')
    return database.session.query(class_)
