// Copyright (c) 2002 Zope Corporation and Contributors.
// All Rights Reserved.
//
// This software is subject to the provisions of the Zope Public License,
// Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
// THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
// WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
// WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
// FOR A PARTICULAR PURPOSE.

// Page design Javascript library

// A library for manipulating objects on a page with object selection,
// context menus, and drag and drop.  Mostly DOM 2 oriented, with bits
// for IE compatibility.
// $Id: pdlib.js,v 1.2 2002/11/21 19:57:39 shane Exp $

// The following variables and functions are documented for use by
// scripts that use this library:
//
//   pd_node_setup
//   pd_selected_item
//   pd_selected_items
//
//   pd_stopEvent()
//   pd_findEventTarget()
//   pd_hideContextMenu()
//   pd_isSelected()
//   pd_select()
//   pd_deselect()
//   pd_clearSelection()
//   pd_setupContextMenu()     -- adds a context menu to an element
//   pd_setupDragUI()          -- adds drag/drop functionality to an element
//   pd_setupDropTarget()      -- turns an element into a drop target
//   pd_setupContextMenuDefinition() -- turns an element into a context menu
//   pd_setupPage()            -- Page initialization (call at bottom of page)
//
// See the documentation for descriptions.
// All other names are subject to change in future revisions.

var pd_open_context_menu = null; // The context menu node being displayed
var pd_drag_event = null;        // A pd_DragEvent object while dragging
var pd_selected_items = null;    // List of selected items
var pd_selected_item = null;     // Non-null when exactly one item is selected
var pd_drag_select_mode = null; // In drag-select mode, -1 or 1, otherwise null
var pd_node_setup = {};          // Object containing node setup functions
var pd_max_contextmenu_width = 250; // Threshold for faulty browsers
var pd_invisible_targets = [];   // A list of normally invisible drop targets

var pd_target_normal_border = "2px solid transparent";
var pd_target_highlighted_border = "2px dotted red";
var pd_target_loading_border = "2px solid green";


function pd_hasAncestor(node, ancestor) {
  var p = node;
  while (p) {
    if (p == ancestor)
      return true;
    p = p.parentNode;
  }
  return false;
}

function pd_stopEvent(e) {
  if (!e)
    e = event;
  if (e.stopPropagation)
    e.stopPropagation();
  else
    e.cancelBubble = true;
  return false;
}

function pd_findEventTarget(e, className, stop_className) {
  // Search for a node of the given class among the ancestors of the
  // target of an event, stopping if stop_className is encountered.
  var node = e.target || e.srcElement;
  while (node) {
    if (node.className == className)
      return node;
    if (stop_className && node.className == stop_className)
      return null;
    node = node.parentNode;
  }
  // Not found.
  return null;
}

function pd_highlight(node, enabled) {
  node.style.color = enabled ? "HighlightText" : "";
  node.style.backgroundColor = enabled ? "Highlight" : "";
}

//
// Context menu functions
//

function pd_showContextMenu(menunode, e) {
  if (!e)
    e = event;
  // Close any open menu
  pd_hideContextMenu();
  var page_w = window.innerWidth || document.body.clientWidth;
  var page_h = window.innerHeight || document.body.clientHeight;
  var page_x = window.pageXOffset || document.body.scrollLeft;
  var page_y = window.pageYOffset || document.body.scrollTop;

  if (menunode.offsetWidth >= pd_max_contextmenu_width) {
    // It's likely that the browser ignored "display: table"
    // and used the full width of the page.  Use a workaround.
    menunode.style.width = pd_max_contextmenu_width;
  }

  // Choose a location for the menu based on where the user clicked
  if (page_w - e.clientX < menunode.offsetWidth) {
    // Close to the right edge
    menunode.style.left = page_x + e.clientX - menunode.offsetWidth - 1;
  }
  else {
    menunode.style.left = page_x + e.clientX + 1;
  }
  if (page_h - e.clientY < menunode.offsetHeight) {
    // Close to the bottom
    menunode.style.top = page_y + e.clientY - menunode.offsetHeight - 1;
  }
  else {
    menunode.style.top = page_y + e.clientY + 1;
  }

  pd_open_context_menu = menunode;
  menunode.style.visibility = "visible";
  return false;
}

function pd_hideContextMenu(e) {
  if (pd_open_context_menu) {
    pd_open_context_menu.style.visibility = "hidden";
    pd_open_context_menu = null;
  }
}

function pd_getContextMenuItem(e) {
  return pd_findEventTarget(e, "context-menu-item", "context-menu");
}

function pd_highlightContextMenuItem(e) {
  if (!e)
    e = event;
  var node = pd_getContextMenuItem(e);
  if (node)
    pd_highlight(node, true);
}

function pd_unhighlightContextMenuItem(e) {
  if (!e)
    e = event;
  var node = pd_getContextMenuItem(e);
  if (node)
    pd_highlight(node, false);
}

function pd_filterContextMenuItems(node) {
  // Execute filter scripts and set the "display" style property
  var i, f, enabled;
  if (node.getAttribute) {
    f = node.getAttribute("filter");
    if (f) {
      enabled = eval(f);
      if (enabled)
        node.style.display = "";
      else
        node.style.display = "none";
    }
  }
  for (i = 0; i < node.childNodes.length; i++)
    pd_filterContextMenuItems(node.childNodes[i]);
}

//
// Drag functions
//

function pd_DragEvent(e, move_func, checkmove_func) {
  this.target = null;
  this.move_func = move_func;
  this.checkmove_func = checkmove_func;
  this.start_x = e.pageX ? e.pageX : e.clientX + document.body.scrollLeft;
  this.start_y = e.pageY ? e.pageY : e.clientY + document.body.scrollTop;
  this.feedback_node = document.getElementById("drag-feedback-box");
  this.began_moving = false;
  this.revealed = [];
}

function pd_unhighlightDropTarget() {
  if (pd_drag_event && pd_drag_event.target) {
    pd_drag_event.target.style.border = pd_target_normal_border;
    pd_drag_event.target = null;
  }
}

function pd_allowDrop(target) {
  if (!pd_drag_event)
    return false;
  var i;
  for (i = 0; i < pd_selected_items.length; i++) {
    if (pd_hasAncestor(target, pd_selected_items[i])) {
      // Don't let the user drag an element inside itself.
      return false;
    }
  }
  if (pd_drag_event.checkmove_func) {
    if (!pd_drag_event.checkmove_func(pd_selected_items, target))
      return false;
  }
  return true;
}

function pd_highlightDropTarget(target) {
  if (pd_allowDrop(target)) {
    pd_unhighlightDropTarget();
    target.style.border = pd_target_highlighted_border;
    pd_drag_event.target = target;
  }
}

function pd_firstDrag(x, y) {
  if (!pd_drag_event)
    return;
  var i, target;
  var feedback_node_style = pd_drag_event.feedback_node.style;
  var item = pd_selected_items[0];  // TODO: expand box to include all items

  pd_drag_event.began_moving = true;
  feedback_node_style.left = x + 5;
  feedback_node_style.top = y + 5;
  feedback_node_style.width = item.offsetWidth - 2;
  feedback_node_style.height = item.offsetHeight - 2;
  feedback_node_style.display = "block";

  // Show some of the normally invisible targets.
  for (i = 0; i < pd_invisible_targets.length; i++) {
    target = pd_invisible_targets[i];
    if (pd_allowDrop(target)) {
      if (pd_drag_event.revealed.push)
        pd_drag_event.revealed.push(target);
      else
        pd_drag_event.revealed = pd_drag_event.revealed.concat([target]);
      target.style.visibility = "visible";
    }
  }
}

function pd_dragging(e) {
  if (!pd_drag_event)
    return;
  if (!e)
    e = event;
  var x = e.pageX ? e.pageX : e.clientX + document.body.scrollLeft;
  var y = e.pageY ? e.pageY : e.clientY + document.body.scrollTop;

  if (!pd_drag_event.began_moving) {
    if (Math.abs(x - pd_drag_event.start_x) <= 3 &&
        Math.abs(y - pd_drag_event.start_y) <= 3) {
      // Didn't move far enough yet.
      return;
    }
    pd_firstDrag(x, y);
  }
  pd_drag_event.feedback_node.style.left = x + 5;
  pd_drag_event.feedback_node.style.top = y + 5;
}

function pd_finishDrag() {
  var i;
  for (i = 0; i < pd_drag_event.revealed.length; i++)
    pd_drag_event.revealed[i].style.visibility = '';

  document.onmousemove = null;
  document.onmouseup = null;
  document.onselectstart = null;
  pd_drag_event.feedback_node.style.display = "none";
  var ev = pd_drag_event;
  pd_drag_event = null;

  if (ev.target) {
    ev.target.style.border = pd_target_loading_border;
    if (ev.move_func)
      ev.move_func(pd_selected_items, ev.target);
  }
}

function pd_startDrag(e, move_func, checkmove_func) {
  if (pd_drag_event) {
    // Already dragging
    return;
  }
  if (!e)
    e = event;
  pd_drag_event = new pd_DragEvent(e, move_func, checkmove_func);
  document.onmousemove = pd_dragging;
  document.onmouseup = pd_finishDrag;
  document.onselectstart = pd_stopEvent;  // IE: Don't start a selection.
  if (e.preventDefault)
    e.preventDefault();  // NS 6: Don't start a selection.
}

//
// Selection management functions
//

function pd_isSelected(node) {
  if (pd_selected_items) {
    for (var i = 0; i < pd_selected_items.length; i++) {
      if (node == pd_selected_items[i]) {
        return true;
      }
    }
  }
  return false;
}

function pd_changedSelection() {
  if (pd_selected_items && pd_selected_items.length == 1)
    pd_selected_item = pd_selected_items[0];
  else
    pd_selected_item = null;
}

function pd_deselect(node) {
  var i, n;
  if (pd_selected_items) {
    var newsel = [];
    // There must be a better way.  This could be slow.
    for (i = 0; i < pd_selected_items.length; i++) {
      n = pd_selected_items[i];
      if (n != node) {
        if (newsel.push)
          newsel.push(n)
        else
          newsel = newsel.concat([n]);
      }
    }
    pd_selected_items = newsel;
    pd_changedSelection();
  }
  pd_highlight(node, false);
}

function pd_select(node) {
  if (!pd_isSelected(node)) {
    if (!pd_selected_items)
      pd_selected_items = [node];
    else if (pd_selected_items.push)
      pd_selected_items.push(node);
    else
      pd_selected_items = pd_selected_items.concat([node]);
  }
  pd_highlight(node, true);
}

function pd_clearSelection() {
  var i, node, n;
  if (pd_selected_items) {
    for (i = 0; i < pd_selected_items.length; i++)
      pd_highlight(pd_selected_items[i], false);
  }
  pd_selected_items = [];
  pd_changedSelection();
}

function pd_dragSelecting(node) {
  if (pd_drag_select_mode == 1)
    pd_select(node);
  else if (pd_drag_select_mode == -1)
    pd_deselect(node);
}

function pd_endDragSelect() {
  pd_drag_select_mode = null;
  document.onmouseup = null;
}

function pd_startDragSelect(v) {
  document.onmouseup = pd_endDragSelect;
  pd_drag_select_mode = v;
}


//
// On-page object management functions
//

function pd_itemOnMousedown(mo, e, move_func, checkmove_func, box) {
  if (!e)
    e = event;
  if (e.button == 0 || e.button == 1) {
    pd_hideContextMenu();
    if (!box)
      box = mo;
    if (e.shiftKey) {
      // Toggle the selected state of this item and start drag select.
      if (pd_isSelected(box)) {
        pd_deselect(box);
        pd_startDragSelect(-1);
      }
      else {
        pd_select(box);
        pd_startDragSelect(1);
      }
    }
    else if (e.ctrlKey) {
      if (pd_isSelected(box))
        pd_deselect(box);
      else
        pd_select(box);
    }
    else {
      if (!pd_isSelected(box)) {
        pd_clearSelection();
        pd_select(box);
      }
      pd_startDrag(e, move_func, checkmove_func);
    }
  }
  return pd_stopEvent(e);
}

function pd_itemOnMouseover(mo, e, box) {
  if (pd_drag_select_mode) {
    pd_dragSelecting(box || mo);
    return pd_stopEvent(e);
  }
}

function pd_itemOnContextMenu(mo, e, contextMenuId, box) {
  if (!e)
    e = event;
  if (!box)
    box = mo;
  if (!pd_isSelected(box)) {
    pd_clearSelection();
    pd_select(box);
  }
  var menu = document.getElementById(contextMenuId);
  if (menu) {
    pd_filterContextMenuItems(menu);
    pd_showContextMenu(menu, e);
    return pd_stopEvent(e);
  }
}

function pd_setupDragUI(mo, move_func, checkmove_func, box) {
  // Adds selection and drag and drop functionality to an element
  function call_onmousedown(e) {
    return pd_itemOnMousedown(mo, e, move_func, checkmove_func, box);
  }
  function call_onmouseover(e) {
    return pd_itemOnMouseover(mo, e, box);
  }
  mo.onmousedown = call_onmousedown;
  mo.onmouseover = call_onmouseover;
  mo.onselectstart = pd_stopEvent;  // IE: Don't start a selection.
}

function pd_setupContextMenu(mo, contextMenuId, box) {
  // Adds context menu functionality to an element
  function oncontextmenu(e) {
    return pd_itemOnContextMenu(mo, e, contextMenuId, box);
  }
  mo.oncontextmenu = oncontextmenu;
}

function pd_documentOnMouseDown() {
  pd_hideContextMenu();
  pd_clearSelection();
}

function pd_setupNodeAndDescendants(node) {
  var i, f;
  if (node.className) {
    f = pd_node_setup[node.className];
    if (f)
      f(node);
  }
  for (i = 0; i < node.childNodes.length; i++) {
    pd_setupNodeAndDescendants(node.childNodes[i]);
  }
}

function pd_setupPage(node) {
  if (!node)
    node = document;
  if (!document.onmousedown)
    document.onmousedown = pd_documentOnMouseDown;
  pd_setupNodeAndDescendants(node);
}

function pd_setupDropTarget(node) {
  function call_highlight() {
    return pd_highlightDropTarget(node);
  }
  node.onmouseover = call_highlight;
  node.onmouseout = pd_unhighlightDropTarget;
  node.onmousedown = pd_stopEvent; // Prevent accidental selection
}

function pd_setupContextMenuDefinition(node) {
  node.onmouseover = pd_highlightContextMenuItem;
  node.onmouseout = pd_unhighlightContextMenuItem;
  node.onmousedown = pd_stopEvent;
  node.onmouseup = pd_hideContextMenu;
}

pd_node_setup['drop-target'] = pd_setupDropTarget;
pd_node_setup['context-menu'] = pd_setupContextMenuDefinition;
