//----------------------------------------------------------------------------
/** 
 * @fileoverview JSON based form validation
 * The method jsonValidate can be used for validate input fields via JSON.
 * The p01/json/xmlhttp.js and p01/json/json.js are used for doing this. 
 *
 * @author Roger Ineichen dev@projekt01.ch
 * @version Alpha, just a concept draft, I'll change this later and we probably
 * use a JQuery based concept. 
 */
//----------------------------------------------------------------------------

/** @private */
function addClassName(ele, clsName) {
  originalStr = ele.className;
  targetStr = " " + clsName;
  replaceStr = "";
  resultStr = originalStr.replace(new RegExp(targetStr, "g"), replaceStr);
  resultStr += " " + clsName;
  ele.className = resultStr;
}

/** @private */
function removeClassName(ele, clsName) {
  originalStr = ele.className;
  targetStr = " " + clsName;
  replaceStr = "";
  resultStr = originalStr.replace(new RegExp(targetStr, "g"), replaceStr);
  ele.className = resultStr;
}

/** @private */
function showValidationError(response) {
	var ele = document.getElementById(response.id);
	if (response.result == 'OK') {
		removeClassName(ele, 'invalide');
		addClassName(ele, 'validated');
	} else {
		removeClassName(ele, 'validated');
		addClassName(ele, 'invalide');
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