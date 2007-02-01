
import os, sys

import ZSQLAlchemy

def initialize(context):
    context.registerClass(
        ZSQLAlchemy.ZSQLAlchemy,
        permission='Add ZSQLAlchemy',
#        icon='pt/index.gif',
        constructors=(ZSQLAlchemy.manage_addZSQLAlchemyForm,
                      ZSQLAlchemy.manage_addZSQLAlchemy),
    )


