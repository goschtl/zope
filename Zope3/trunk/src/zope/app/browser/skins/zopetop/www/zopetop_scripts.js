// Copyright (c) 2002 Zope Corporation and Contributors.
// All Rights Reserved.
//
// This software is subject to the provisions of the Zope Public License,
// Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
// THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
// WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
// WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
// FOR A PARTICULAR PURPOSE.

// ZopeTop scripts (requires pdlib)

function Box_add() {
  window.alert("Add box is not implemented yet.");
}

function Boxes_copy() {
  window.alert("Copy is not implemented yet.  Objects: " + pd_selected_items);
}

function Boxes_cut() {
  window.alert("Cut is not implemented yet.  Objects: " + pd_selected_items);
}

function Boxes_paste() {
  window.alert("Paste is not implemented yet.  Objects: " + pd_selected_items);
}

function Boxes_remove() {
  var i, node;
  for (i = 0; i < pd_selected_items.length; i++) {
    node = pd_selected_items[i];
    node.style.display = "none";
  }
}

function Boxes_move(pd_selected_items, target_node) {
  var i, node, peer;
  if (target_node.parentNode.className == 'box-holder')
    peer = target_node.parentNode;
  else
    peer = target_node;
  for (i = 0; i < pd_selected_items.length; i++) {
    node = pd_selected_items[i];
    node.parentNode.removeChild(node);
    peer.parentNode.insertBefore(node, peer);
    target_node.style.border = "2px solid transparent";
  }
}

function Boxes_checkmove(pd_selected_items, target_node) {
  return true;
}

function zopetop_findDescendant(node, className) {
  // Returns a descendant with the given class name, or null.
  if (node.className == className)
    return node;
  var i, c;
  for (i = 0; i < node.childNodes.length; i++) {
    c = zopetop_findDescendant(node.childNodes[i], className);
    if (c != null)
      return c;
  }
  return null;
}

function zopetop_setupBoxHolder(holder) {
  var boxtop = zopetop_findDescendant(holder, "boxtop") || holder;
  pd_setupDragUI(boxtop, Boxes_move, Boxes_checkmove, holder);
  pd_setupContextMenu(boxtop, 'box-context-menu', holder);
}

pd_node_setup['box-holder'] = zopetop_setupBoxHolder;

function zopetop_setupDropTarget(node) {
  pd_setupDropTarget(node);
  if (pd_invisible_targets.push)
    pd_invisible_targets.push(node);
  else
    pd_invisible_targets = pd_invisible_targets.concat([node]);
}

pd_node_setup['drop-target'] = zopetop_setupDropTarget;

