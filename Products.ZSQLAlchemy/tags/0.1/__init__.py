##########################################################################
# ZSQLAlchemy
#
# (C) 2007, ZOPYX Ltd & Co. KG
# D-72070 Tuebingen, Germany
# www.zopyx.com, info@zopyx.com
#
# Written by Andreas Jung
#
# ZSQLAlchemy is published under the Zope Public License 2.1 (ZPL 2.1)
##########################################################################


import ZSQLAlchemy

def initialize(context):
    context.registerClass(
        ZSQLAlchemy.ZSQLAlchemy,
        permission='Add ZSQLAlchemy',
#        icon='pt/index.gif',
        constructors=(ZSQLAlchemy.manage_addZSQLAlchemyForm,
                      ZSQLAlchemy.manage_addZSQLAlchemy),
    )


