##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################

"""
    Interfaces for Workflow Process Definition.
"""

from Interface import Interface

class IWorkflowProcessInstance( Interface ):
    """
        Interface for workflow process definition.
    """


    def getStatus():
        """
           Report the status
        """
        pass

    
    def setActive():
        """
           Change the status to Active according to the state machine
        """
        pass


    def setCompleted():
        """
           Change the status to Completed according to the state machine
        """
        pass

    
    def listWorkitems():
        """
           List all contained workitems
        """
        pass
    

    def listActiveWorkitems():
        """
           List contained Active workitems
        """
        pass


    def listFailedWorkitems():
        """
          List contained Failed workitem
        """
        pass

    
