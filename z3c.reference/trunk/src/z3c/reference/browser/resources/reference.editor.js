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
    var query = $j($j("#viewrefeditor_formdata")[0]).formSerialize();
    var data = $j.ajax({url:url, data:query, async:false}).responseText;
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
                'target': targetStr,
                'name': name}
    $j("#editorSearch").load("viewReferenceEditorSearch", settings); 
}

function loadEditorEdit(targetStr, extra) {
    currentTargetUid = targetStr;

    var url = "viewReferenceEditorEdit";
    url += "?settingName="+settingNameStr;
    url += "&target=" + targetStr;
    if (extra){
        url += "&" + extra;
    }

    
    $j.get(url, function (data){
            var submit_btn = "<input type='button' class='submit' value='save' onclick='saveAndClose()' />";
            $j("#editorEdit").empty().append(data).append(submit_btn);
            try {
                executeJavascript();
            } catch(e) {}
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
