// user selects an item
//function setIntId(uid) {
//    // reset values
//    $("textarea").val("");
//    $("input[@type=text]").val("");
//    // set initid of selected item
//    $("input[@name=intid]").val(uid);
//    // highlight selected item
//    $("a").attr("style", "");
//    $("a[@href*=" + uid + "]").attr("style","background-color: #888");
//}

function loadEditorSearch() {
    settings = {'settingName': settingNameStr,
                'target': targetStr,
                'view': viewStr,
                'title': titleStr,
                'description': descriptionStr}
    $.get("viewReferenceEditorSearch", settings, function () {
        $("#editorSearch").append($(data));
    });
}

function loadEditorEdit(targetStr) {
    settings = {'settingName': settingNameStr,
                'target': targetStr,
                'view': viewStr,
                'title': titleStr,
                'description': descriptionStr}
    $.get("viewReferenceEditorEdit", settings, function () {
        $("#editorEdit").append($(data));
    });
}

// initialize on dom ready
$(document).ready(function(){
    // load search form
    loadEditorSearch();
	
    // load edit form
    if (targetStr) {
        loadEditorEdit(targetStr);
    }
});
