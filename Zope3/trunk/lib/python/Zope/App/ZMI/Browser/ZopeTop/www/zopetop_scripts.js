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
  var i, node;
  for (i = 0; i < pd_selected_items.length; i++) {
    node = pd_selected_items[i];
    node.parentNode.removeChild(node);
    target_node.parentNode.insertBefore(node, target_node);
    target_node.style.border = "2px solid transparent";
  }
}

function Boxes_checkmove(pd_selected_items, target_node) {
  return true;
}

function setupBox(node) {
  pd_setupDragUI(node, Boxes_move, Boxes_checkmove);
  pd_setupContextMenu(node, 'box-context-menu');
}

pd_node_setup['box'] = setupBox;

