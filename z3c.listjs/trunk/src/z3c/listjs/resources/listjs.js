// create the top-level Z3C namespace if needed
if (typeof Z3C == "undefined" || !Z3C) {
    var Z3C = {};
}

// create a new namespace (under Z3C)
Z3C.namespace = function(name) {
    var ns = Z3C;
    var parts = name.split(".");
    if (parts[0] == "Z3C") {
        parts = parts.slice(1);
    }
    for (var i = 0; i < parts.length; i++) {
        var part = parts[i];
        ns[part] = ns[part] || {};
        ns = ns[part];
    }
    return ns;
};

(function() {
    Z3C.namespace('listjs');

    var disconnected_editor_ids = [];

    // return true if string starts with a prefix
    var startswith = function(s, prefix) {
        return (s.substring(0, prefix.length) == prefix);
    };

    // check whether a particular object is a number
    var isNumber = function(o) {
        return typeof o === 'number' && isFinite(o);
    };

    // change all numbers in a string with a dotted name to a new number
    // also renumber remove_X
    var renumber = function(s, nr) {
        var i;
        var fragment;
        var fragments = s.split('.');
        var result = [];
        for (i = 0; i < fragments.length; i++ ) {
            fragment = fragments[i];
            if (isNumber(parseInt(fragment))) {
                result[result.length] = nr.toString();
            } else if (startswith(fragment, 'remove_')) {
                result[result.length] = 'remove_' + nr.toString();
            } else {
                result[result.length] = fragment;
            }
        };
        return result.join('.');
    };

    var renumberScript = function(s, nr, prefix) {
        var tomatch = new RegExp(prefix + '[^"\']*', 'g');
        var potentials = s.match(tomatch);
        if (potentials == null) {
            return s; // nothing to replace
        }
        var original = potentials[0];
        var renumbered = renumber(original, nr);
        return s.replace(original, renumbered);
    };

    // simplistic implementation that doesn't understand 
    // multiple classes per element
    var getElementsByClassName = function(class_name, root_el, tag) {
        tag = tag || '*';
        
        var result = [];
        var elements = root_el.getElementsByTagName(tag);
        
        for (var i = 0, len = elements.length; i < len; ++i) {
            if (elements[i].className == class_name) {
                result[result.length] = elements[i];
            }
        }
        return result;
    };

    // number all relevant attributes under el with nr
    var updateNumbers = function(el, nr, prefix) {
        // optimization - skip non-element nodes (ELEMENT_NODE 1)
        if (el.nodeType != 1) {
            return;
        }

        // if this is a script tag, do textual replace
        if (el.tagName.toLowerCase() == 'script') {
            el.text = renumberScript(el.text, nr, prefix);
            return;
        }

        var i;
        var attributes = ['id', 'name', 'for'];
        for (i = 0; i < attributes.length; i++) {
            var attr = el.getAttribute(attributes[i]);
            if (attr && startswith(attr, prefix)) {
                el.setAttribute(attributes[i], renumber(attr, nr));
            }
        }
        
        var onclick_attr = el.getAttribute('onclick');
        if (onclick_attr) {
            el.setAttribute('onclick', renumberScript(onclick_attr, nr, prefix));
        }

        // recursion
        var node = el.firstChild;
        while (node) {
            updateNumbers(node, nr, prefix);
            node = node.nextSibling;
        }   
    };
    
    // update all numbers in el root
    var updateAllNumbers = function(prefix) {
        var table_el = document.getElementById(prefix + '.table');
        // update numbering in table
        var els = getElementsByClassName('list_item', table_el, 'tr');
        var i;
        for (i = 0; i < els.length; i++) {
            updateNumbers(els[i], i, prefix);
            runScripts(els[i]);
        }
        // update count
        var count_el = document.getElementById(prefix + '.count');
        count_el.value = els.length;
    };
    
    // disconnect all editors in affected elements
    var disconnectEditors = function(affected_elements) {
       // if tinyMCE is installed, disconnect all editors
        if (tinyMCE) {
            //tinyMCE.triggerSave();
            disconnected_editor_ids = [];
            for (var n in tinyMCE.editors) {
                var inst = tinyMCE.editors[n];
                if (!inAffectedElements(inst.getElement(), 
                                        affected_elements)) {
                    continue;
                }
                disconnected_editor_ids.push(inst.id);
                tinyMCE.execCommand('mceFocus', false, inst.id);
                tinyMCE.execCommand('mceRemoveControl', false, inst.id);
            }
        }
    };

    // reconnect all editors that aren't reconnected already
    var reconnectEditors = function() {
        // reconnect all editors
        if (tinyMCE) {
           for (i = 0; i < disconnected_editor_ids.length; i++) {
               var editor_id = disconnected_editor_ids[i];
               if (!tinyMCE.get(editor_id)) {
                   tinyMCE.execCommand('mceAddControl', false, editor_id);
               }
           }
        }
    };

    // return true if el is inside one of affected_elements
    var inAffectedElements = function(el, affected_elements) {
        for (var i = 0; i < affected_elements.length; i++) {
            if (isAncestor(affected_elements[i], el)) {
                return true;
            }
        }
        return false;
    };

    // return true if a is an ancestor of b
    var isAncestor = function(a, b) {
        while (b) {
            if (a === b) {
                return true;
            }
            b = b.parentNode;
        }
        return false;
    }


    // run all embedded scripts (after setting innerHTML)
    // see http://brightbyte.de/page/Loading_script_tags_via_AJAX
    // combined with 
    // http://caih.org/open-source-software/loading-javascript-execscript-and-testing/
    // to eval in the global scope
    var runScripts  = function(e) { 
        if (e.nodeType != 1) {
            return;
        }
        
        // run any script tag
        if (e.tagName.toLowerCase() == 'script') {
            if (window.execScript) {
                window.execScript(e.text);
            } else {
                with (window) {
                    window.eval(e.text);
                }
            }
        } else {
            var n = e.firstChild;
            while (n) {
                if (n.nodeType == 1) {
                    runScripts(n);
                }
                n = n.nextSibling;
            }
        }
    };

    // add a new repeating element to the list
    Z3C.listjs.add = function(prefix) {
        var table_el = document.getElementById(prefix + '.table');
        var template_el = document.getElementById(prefix + '.template');
        var template_text = template_el.value;
        var buttons_el = document.getElementById(prefix + '.buttons');

        // note that some DOM manipulation is needed as IE cannot
        // use innerHTML on tr directly. Instead we create the td
        // and put the widget contents in that.
        var new_tr = document.createElement('tr');
        new_tr.className = 'list_item';
        buttons_el.parentNode.insertBefore(new_tr, buttons_el);
        var td1 = document.createElement('td');
        var td2 = document.createElement('td');
        var td3 = document.createElement('td');
        new_tr.appendChild(td1);
        new_tr.appendChild(td2);
        new_tr.appendChild(td3);
        var cb = document.createElement('input');
        cb.className = 'editcheck';
        cb.type = 'checkbox';
        cb.name = prefix + '.remove_0';
        td1.appendChild(cb);
        td2.innerHTML = template_text;

        // up and down arrows
        var div_up = document.createElement('div');
        var div_down = document.createElement('div');
        var a_up = document.createElement('a');
        var a_down = document.createElement('a');
        a_up.className = 'up_button';
        a_down.className = 'down_button';
        a_up.onclick = function() {
            Z3C.listjs.up(prefix, this);
        };
        a_down.onclick = function() {
            Z3C.listjs.down(prefix, this);
        };
        td3.appendChild(div_up);
        td3.appendChild(div_down);
        div_up.appendChild(a_up);
        div_down.appendChild(a_down);
        
        updateAllNumbers(prefix);
    };
   
    // remove all selected repeating elements from the list
    Z3C.listjs.remove = function(prefix) {
        var table_el = document.getElementById(prefix + '.table');

        // find all elements that are checked
        var els = getElementsByClassName('editcheck', table_el, 'input');
        var i;
        var to_remove = [];
        for (i = 0; i < els.length; i++) {
            if (els[i].checked) {
                // remove the tr (two levels up from the input box)
                to_remove[to_remove.length] = els[i].parentNode.parentNode;
            }
        }
        // now actually remove them
        for (i = 0; i < to_remove.length; i++) {
            to_remove[i].parentNode.removeChild(to_remove[i]);
        }
        
        updateAllNumbers(prefix);
    };

    
    Z3C.listjs.up = function(prefix, el) {
        while (el.className != 'list_item') {
            el = el.parentNode;
        }
        var previous_el = el.previousSibling;
        while (previous_el != null && previous_el.className != 'list_item') {
            previous_el = previous_el.previousSibling;
        }
        // first list element, no move possible
        if (previous_el == null) {
            return;
        }

        disconnectEditors([el, previous_el]);

        previous_el.parentNode.insertBefore(el, previous_el);
        updateAllNumbers(prefix);

        reconnectEditors();
    };

    Z3C.listjs.down = function(prefix, el) {
        while (el.className != 'list_item') {
            el = el.parentNode;
        }
        var next_el = el.nextSibling;
        while (next_el != null && next_el.className != 'list_item') {
            next_el = next_el.nextSibling;
        }
        // last list element, no move possible
        if (next_el == null) {
            return;
        }
        disconnectEditors([el, next_el]);

        next_el.parentNode.insertBefore(el, next_el.nextSibling);
        updateAllNumbers(prefix);

        reconnectEditors();
    };
    
})();
