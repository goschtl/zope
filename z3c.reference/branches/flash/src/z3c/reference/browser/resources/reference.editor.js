var settingName = '';

// user selects an item
function setIntId(uid) {
    // reset values
    $("textarea").val("");
    $("input[@type=text]").val("");
    // set initid of selected item
    $("input[@name=intid]").val(uid);
    // highlight selected item
    $("a").attr("style", "");
    $("a[@href*=" + uid + "]").attr("style","background-color: #888");
}

function loadEditorSearch() {
    $.get("viewReferenceEditorSearch", {'settingName':settingName}, function () {
        $("#editorSearch").append($(data));
    });
}

function loadEditorEdit() {
    $.get("viewReferenceEditorEdit", {'settingName':settingName}, function () {
        $("#editorEdit").append($(data));
    });
}

// initialize on dom ready
$(document).ready(function(){
    // load search form
    loadEditorSearch();
	
    // load edit form
    loadEditorEdit();
});