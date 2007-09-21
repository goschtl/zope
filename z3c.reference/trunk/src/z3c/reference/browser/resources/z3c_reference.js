/*
  this file is included into the main window. it opens the
  reference editor popup when required.
*/

var profiles = {
		window:
		{
			height:550,
			width:800,
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
function setReferenceInput(name, targetUid, query, title){
   $j("input[@name="+name+".target]").val(targetUid);
   $j("input[@name="+name+".formData]").val(query);
   $j("span[@id="+name+".title]").empty().append(title);

   var a = $j("a[@name="+name+"]");
   var url = a.attr("href");
   url = url.split('?')[0]
         + '?target=' + $j("input[@name="+name+".target]").val()
         + '&settingName=' + $j("input[@name="+name+".settingName]").val()
         + '&name=' + name;
   a.attr('href', url);
}


function getReferenceInputData(name){
    return $j("input[@name="+name+".formData]").val()
}

