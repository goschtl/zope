
// Composite editing scripts (based on PDLib)

function composite_move(selected_items, target_node) {
  var f, i, path, sources, s;
  f = document.forms.modify_composites;
  i = target_node.getAttribute("target_index");
  path = target_node.getAttribute("target_path");
  f.elements.move_target_index.value = i;
  f.elements.move_target_path.value = path;

  sources = "";
  for (i = 0; i < selected_items.length; i++) {
    s = selected_items[i].getAttribute("source_path");
    if (s) {
      if (sources)
        sources = sources + ":" + s;
      else
        sources = s;
    }
  }
  f.elements.move_source_paths.value = sources;
  f.submit();
}

function composite_checkmove(selected_items, target_node) {
  var target_path, source_path, i;
  target_path = target_node.getAttribute("target_path");
  for (i = 0; i < selected_items.length; i++) {
    source_path = selected_items[i].getAttribute("source_path");
    if (source_path) {
      source_path = source_path + "/";  // Terminate on full names
      // window.status = "From " + source_path + " to " + dest_path;
      if (target_path.slice(0, source_path.length) == source_path) {
        // Don't allow a parent to become its own child.
        return false;
      }
    }
  }
  return true;
}

function composite_delete(selected_items) {
  var f, i, s, sources;
  if (!selected_items)
    return;
  f = document.forms.modify_composites;
  sources = "";
  for (i = 0; i < selected_items.length; i++) {
    s = selected_items[i].getAttribute("source_path");
    if (s) {
      if (sources)
        sources = sources + ":" + s;
      else
        sources = s;
    }
  }
  f.elements.delete_source_paths.value = sources;
  f.submit();
}

function composite_highlightTarget(node, state) {
  if (state == 0)
    node.style.background = "inherit";
  else if (state == 1)
    node.style.background = "black";
  else if (state == 2)
    node.style.background = "green";
}


function setUpSlotTarget(node) {
  pd_setupDropTarget(node, 0, composite_highlightTarget);
  pd_setupContextMenu(node, 'slot-target-context-menu', null, true);
}

pd_node_setup['slot_target'] = setUpSlotTarget;


function setUpSlotElement(node) {
  pd_setupDragUI(node, composite_move, composite_checkmove);
  pd_setupContextMenu(node, 'slot-element-context-menu', null, true);
}

pd_node_setup['slot_element'] = setUpSlotElement;

