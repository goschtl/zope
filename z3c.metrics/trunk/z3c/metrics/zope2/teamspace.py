from zope import component

from Products.CMFCore import utils as cmf_utils

from Products.remember import interfaces as remember_ifaces
from Products.TeamSpace.interfaces import (
    membership as membership_ifaces)
from Products.TeamSpace.interfaces import space as space_ifaces

from z3c.metrics import interfaces

@component.adapter(membership_ifaces.ITeamMembership,
                   interfaces.IChangeScoreEvent)
def dispatchToSpaces(membership, event):
    for space in membership.getTeam().getTeamSpaces():
        for _ in component.subscribers(
            [membership, event, space], None):
            pass # Just make sure the handlers run

@component.adapter(space_ifaces.ISpace,
                   interfaces.IBuildScoreEvent)
def dispatchToTeamMemberships(space, event):
    for team in space.getSpaceTeams():
        for membership in team.getMemberships():
            for _ in component.subscribers(
                [membership, event, space], None):
                pass # Just make sure the handlers run

@component.adapter(membership_ifaces.ITeamMembership,
                   interfaces.IChangeScoreEvent)
def dispatchToMember(membership, event):
    for _ in component.subscribers(
        [membership, event, membership.getMember()], None):
        pass # Just make sure the handlers run
    
@component.adapter(remember_ifaces.IReMember,
                   interfaces.IBuildScoreEvent)
def dispatchToMemberMemberships(member, event):
    portal_teams = cmf_utils.getToolByName(member, 'portal_teams')
    for membership in portal_teams.getTeamMembershipsFor(
        member.getId()):
        for _ in component.subscribers(
            [membership, event, member], None):
            pass # Just make sure the handlers run
