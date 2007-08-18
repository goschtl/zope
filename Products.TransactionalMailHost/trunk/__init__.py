##########################################################################
# A transaction-aware Mailhost implementation based on zope.sendmail
#
# (C) Zope Corporation and Contributors
# Written by Andreas Jung for ZOPYX Ltd. & Co. KG, Tuebingen, Germany
##########################################################################


from AccessControl.Permissions import add_mailhost_objects

def initialize(context):

    from mailhost import (MailHost, manage_addMailHost, manage_addMailHostForm)

    context.registerClass(MailHost, 
                          constructors=(manage_addMailHostForm, 
                                        manage_addMailHost),
                          icon='www/MailHost_icon.gif',
                          permission=add_mailhost_objects)
