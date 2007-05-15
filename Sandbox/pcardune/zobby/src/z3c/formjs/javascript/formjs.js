function fjs_displayToEdit(element_id){
  element = $(document.getElementById(element_id));
  element.show();
  element.prev().hide();
  element.next().val('Save').unbind("click").click(function (){fjs_editToDisplay(element_id)});
  element.focus();
}

function fjs_editToDisplay(element_id){
  element = $(document.getElementById(element_id));
  element.hide();
  element.prev().text(element.val()).show();
  element.next().val('Change').unbind("click").click(function (){fjs_displayToEdit(element_id)});
}
