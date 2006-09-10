# -*- coding: UTF-8 -*-

from BTrees.OOBTree import OOBTree

from persistent import Persistent
from zope.app.container.contained import Contained

from zope.interface import implements

from z3c.wfmcpersistent.interfaces import IProcessDefinitionRegistry


class ProcessDefinitionRegistry(object):
	"""ProcessDefinitionRegistry implementations."""

	implements(IProcessDefinitionRegistry)

	def __init__(self):
		"""ProcessDefinitionRegistry constructor."""
		super(ProcessDefinitionRegistry, self).__init__()

		self._processdefs = OOBTree()

	def addProcessDefinition(self, processDefinition):
		"""Add a new process definition.
		the ID will be the processDefinition.id"""
		self._processdefs[processDefinition.id]=processDefinition

	def getProcessDefinition(self, id):
		"""Returns a definition given its id.
		
		Raise a KeyError if no process definition is available.
		"""
		return self._processdefs[id]

	def getProcessDefinitions(self):
		"""Returns all process definitions."""
		return list(self._processdefs.values())
	
	def getProcessDefinitionIDs(self):
		"""Returns all process definition IDs."""
		return list(self._processdefs.keys())

	def delProcessDefinition(self, id):
		"""Del a process definition given its ID."""
		del self._processdefs[id]


class GlobalProcessDefinitionRegistry(ProcessDefinitionRegistry):
	"""Global IWorkflowUtility implementation."""

globalProcessDefinitionRegistry = GlobalProcessDefinitionRegistry()


class LocalProcessDefinitionRegistry(ProcessDefinitionRegistry, Contained,
									 Persistent):
	"""Local ProcessDefinitionRegistry utility implementation."""
	
