// change the status of the matrix table
function changeMatrix(e) {
  var ele = e? e: window.event;
  var id = ele.getAttribute('id');
  var name = ele.getAttribute('name');
  var label = ele.parentElement;
  var center = label.parentElement;
  var td = center.parentElement;
  resetMatrixCSS(name);
  if (td.className != "default") {
    td.className = "changed";
  }
}

function resetMatrixCSS(name) {
  var inputFields = document.getElementsByTagName('input');
  for (var i = 0; i < inputFields.length; i++) {
    var field = inputFields[i];
    if (field.getAttribute('name') == name) {
      td = field.parentElement.parentElement.parentElement;
      if (td.className != "default") {
        td.className = "";
      }
    }
  }
}