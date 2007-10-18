/*
  this file is included in the reference editor popup window and
  handles the editor and the communication with the main window
  (window.opener)
 */

// uses jQuery in noConflict mode to work properly with Mochikit
var $j = jQuery.noConflict();

var currentTargetUid = -1;

function saveAndClose(){
    // call the verify page

    var url = "viewReferenceValidator";
    url += "?settingName="+settingNameStr;
    url += "&target=" + currentTargetUid;
    var query = $j($j("form")[0]).formSerialize();
    var data = $.ajax({url:url, data:query, async:false}).responseText;
    if (data == 'Ok') {
        // The input is verified and Ok :
        var title = $j("input[@id=form.title]").val();
        window.opener.setReferenceInput(name, currentTargetUid, query, title);
        window.close();
    } else {
        // The input has errors: inject the result with the errors
        var submit_btn = "<input type='button' class='submit' value='save' onclick='saveAndClose()' />";
        $j("#editorEdit").empty().append(data).append(submit_btn);
    }
}

function loadEditorSearch() {
    settings = {'settingName': settingNameStr,
                'target': targetStr}
    $.get("viewReferenceEditorSearch", settings, function (data) {
            $j("#editorSearch").empty().append($j(data));
    });
}

function loadEditorEdit(targetStr, extra) {
    currentTargetUid = targetStr;

    var url = "viewReferenceEditorEdit";
    url += "?settingName="+settingNameStr;
    url += "&target=" + targetStr;
    if (extra){
        url += "&" + extra;
    }

    $.get(url, function (data){
        var submit_btn = "<input type='button' class='submit' value='save' onclick='saveAndClose()' />";
        $j("#editorEdit").empty().append(data).append(submit_btn);
    });
}

// initialize on dom ready
$j(document).ready(function(){
    // load search form
    if ($j("#editorSearch")){
        loadEditorSearch();
    }
	
    // load edit form
    if (targetStr) {
        loadEditorEdit(targetStr, formdata);
    }
});
