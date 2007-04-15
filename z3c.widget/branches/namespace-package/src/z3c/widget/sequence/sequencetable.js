function sequencetable_moveChildren(srcNode, destNode){
	var count = 0;
	while(srcNode.hasChildNodes()){
		destNode.appendChild(srcNode.firstChild);
		count++;
	}
	return count;
}

function sequencetable_copyChildren(srcNode, destNode){
	var clonedNode = srcNode.cloneNode(true);
	return sequencetable_moveChildren(clonedNode, destNode);
}

function sequencetable_addRow(sPrefix) {
  var sTableID = sPrefix+".tbody";
  var sRowID = sPrefix+"_row#_default_rowid_";
  var tbodyElem = document.getElementById(sTableID);
  var oRow = document.getElementById(sRowID);
  
  var trElem, tdElem;
  trElem = tbodyElem.insertRow(tbodyElem.rows.length);
  var sHtml = new String(oRow.innerHTML);
  
  sequencetable_copyChildren(oRow, trElem);
  
  var oCount = document.getElementById(sPrefix+".count");
  var nMaxLen = Number(document.getElementById(sPrefix+".max_length").value);
  var sNewId = oCount.value;
  oCount.value = String(Number(oCount.value)+1);
  
  if (nMaxLen > 0){
    if (Number(oCount.value) >= nMaxLen) {
      var oAddButton = document.getElementById(sPrefix+".addbutton");
      oAddButton.disabled = true;
    }
  }
  
  var sNewtrId = oRow.id.replace(/_default_rowid_/g, sNewId);
  
  trElem.id = oRow.id;
  
  sequencetable_reName(trElem, "_default_rowid_", sNewId);
  
  return false;
}

function sequencetable_replChild(startNode, oRegEx, sRepl){
  try {
    startNode.id = startNode.id.replace(oRegEx, sRepl);
  } catch(E) {}
  try {
    startNode.name = startNode.name.replace(oRegEx, sRepl);
  } catch(E) {}
  //replacing in innerHTML breaks havoc
  //try {
  //  var si = startNode.innerHTML;
  //  var aMatch = si.match(oRegEx);
  //  startNode.innerHTML = startNode.innerHTML.replace(oRegEx, sRepl);
  //} catch(E) {}
  
  for (var i = 0; i < startNode.childNodes.length; i++) {
    sequencetable_replChild(startNode.childNodes[i], oRegEx, sRepl);
  }
}

function sequencetable_reName(node, sOldID, sNewID){
  var regexp = eval("/"+sOldID+"/g");
  sequencetable_replChild(node, regexp, sNewID);
}

function sequencetable_delRow(oCell, sPrefix) {
  var oCount = document.getElementById(sPrefix+".count");
  var nCount = Number(oCount.value);
  var nMinLen = Number(document.getElementById(sPrefix+".min_length").value);
  
  if (nCount <= nMinLen) {
    //alert("Cannot remove any more items!");
    return false;
  }
  
  var node = oCell;
  var regexp = eval("/"+sPrefix+"_row#(\\d+)/");
  while (node.id.search(regexp) < 0) {
    node = node.parentNode;
  }
  var oRow = node;
  var sTableID = sPrefix+".tbody";
  var tbodyElem = document.getElementById(sTableID);
  var aMatch = node.id.match(/_row#(\d+)/);
  var nToDel = Number(aMatch[1]);
  oRow.parentNode.removeChild(oRow);
  
  for (var i = nToDel+1; i < nCount; i++) {
    sequencetable_reName(tbodyElem, sPrefix+"_row#"+i, sPrefix+"_row#"+(i-1));
    sequencetable_reName(tbodyElem, sPrefix+"."+i+".", sPrefix+"."+(i-1)+".");
  }
  
  oCount.value = String(nCount-1);
  
  var oAddButton = document.getElementById(sPrefix+".addbutton");
  oAddButton.disabled = false;
  
  return false;
}