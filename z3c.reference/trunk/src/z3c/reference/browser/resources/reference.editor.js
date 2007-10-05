/*
  this file is included in the reference editor popup window and
  handles the editor and the communication with the main window
  (window.opener)
 */

var currentTargetUid = -1;

function saveAndClose(){
    // call the verify page

    var url = "viewReferenceValidator";
    url += "?settingName="+settingNameStr;
    url += "&target=" + currentTargetUid;
    var query = $($("form")[0]).formSerialize();
    var data = $.ajax({url:url, data:query, async:false}).responseText;
    if (data == 'Ok') {
        // The input is verified and Ok :
        var title = $("input[@id=form.title]").val();
        window.opener.setReferenceInput(name, currentTargetUid, query, title);
        window.close();
    } else {
        // The input has errors: inject the result with the errors
        var submit_btn = "<input type='button' class='submit' value='save' onclick='saveAndClose()' />";
        $("#editorEdit").empty().append(data).append(submit_btn);
    }
}

function loadEditorSearch() {
    settings = {'settingName': settingNameStr,
                'target': targetStr,
                'view': viewStr,
                'title': titleStr,
                'description': descriptionStr}
    $.get("viewReferenceEditorSearch", settings, function (data) {
            $("#editorSearch").empty().append($(data));
    });
}

function loadEditorEdit(targetStr) {
    currentTargetUid = targetStr;

    var url = "viewReferenceEditorEdit";
    url += "?settingName="+settingNameStr;
    url += "&target=" + targetStr;
    url += "&" + window.opener.getReferenceInputData(name);

    $.get(url, function (data){
        var submit_btn = "<input type='button' class='submit' value='save' onclick='saveAndClose()' />";
        $("#editorEdit").empty().append(data).append(submit_btn);
    });
}

// initialize on dom ready
$(document).ready(function(){
    // load search form
    if ($("#editorSearch")){
        loadEditorSearch();
    }
	
    // load edit form
    if (targetStr) {
        loadEditorEdit(targetStr);
    }
});
