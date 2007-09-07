var profiles = {
		window:
		{
			height:550,
			width:500,
			status:0,
            scrollbars:1,
            resizable:1
		}
	};

// uses jQuery in noConflict mode to work properly with Mochikit
var $j = jQuery.noConflict();

// bind links to popupwindow function 
$j(document).ready(function(){
  $j("a.popupwindow").popupwindow(profiles);
});

// called by popupwindow to write formdata back to opener
// parameter elementid: input name in which to write into
// parameter value: formdata string
function setInput(elementid, value) {
    $j("input[@name="+elementid+"]").val(value);
}