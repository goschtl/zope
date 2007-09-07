function loadEditorSearch() {
    settings = {'settingName': settingNameStr,
                'target': targetStr,
                'view': viewStr,
                'title': titleStr,
                'description': descriptionStr}
    $.get("viewReferenceEditorSearch", settings, function () {
        $("#editorSearch").empty().append($(data));
    });
}

function loadEditorEdit(targetStr) {
    settings = {'settingName': settingNameStr,
                'target': targetStr,
                'view': viewStr,
                'title': titleStr,
                'description': descriptionStr}
    $.get("viewReferenceEditorEdit", settings, function () {
        $("#editorEdit").empty().append($(data));
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
