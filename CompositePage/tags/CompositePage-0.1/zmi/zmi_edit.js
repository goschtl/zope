
// ZMI-specific editing scripts.  Referenced by zmi/bottom.pt.
// The variable "zmi_transformer_url" is provided by zmi/header.pt.

function zmi_edit(element) {
  var path = escape(element.getAttribute("source_path"));
  document.location = zmi_transformer_url + "/showElement?path=" + path;
}

function zmi_add(target) {
  // Note that target_index is also available, but the ZMI can't
  // make use of it easily.
  var path = escape(target.getAttribute("target_path"));
  document.location = zmi_transformer_url + "/showSlot?path=" + path;
}

