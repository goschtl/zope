//----------------------------------------------------------------------------
/** 
 * @fileoverview JSON based form validation
 * The method jsonValidate can be used for validate input fields via JSON.
 * The p01/json/xmlhttp.js and p01/json/json.js are used for doing this. 
 *
 * @author Roger Ineichen dev@projekt01.ch
 * @version Alpha 0.1. I'll change the implementation and add options 
 */
//----------------------------------------------------------------------------

/** @private */
function showValidationError(response) {
    // will get changed to JQuery call including options for the element id, ri
	var ele = document.getElementById(response.id);
	if (response.result == 'OK') {
	    $(ele).removeClass('invalide');
	    $(ele).addClass('validated');
	} else {
	    $(ele).addClass('invalide');
	    $(ele).removeClass('validated');
	}
}


//----------------------------------------------------------------------------
// public API
//----------------------------------------------------------------------------
/**
 * validate a input field with a JSON call.
 * @param {string} id dom element id
 * @param {string} value of the input field
 * @return uses the built in showValidationError method.
 */
function jsonValidate(id, value) {
	var url = viewURL;
	var jsonProxy = getJSONRPCProxy(url);
	jsonProxy.addMethod('jsonValidate', showValidationError);
	jsonProxy.jsonValidate(id, value);
}

/**
 * validate a input field with a JSON call.
 * @return JQuery, uses the built in showValidationError callback.
 */
jQuery.fn.jsonValidate = function() {
    // Implement options for element id and callback etc. ri
    return this.each(function(){
        $(this).blur(function(){
        	var url = viewURL;
        	var id = $(this).attr("id");
        	var value = $(this).val();
        	var jsonProxy = getJSONRPCProxy(url);
        	jsonProxy.addMethod('jsonValidate', showValidationError);
        	jsonProxy.jsonValidate(id, value);
        });

    });
};
