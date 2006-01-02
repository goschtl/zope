// ===========================================================================
// WINDOW MANAGER
// ===========================================================================

var windowManager = {
  offset: function(element) {
    var offset = {}
    element = $(element)
    offset.top = element.offsetTop
    offset.left = element.offsetLeft
    while(element = element.offsetParent) {
      offset.top += element.offsetTop
      offset.left += element.offsetLeft
    }
    return offset
  },

  size: function(element) {
    var size = {}
    element = $(element)
    size.width = element.clientWidth
    size.height = element.clientHeight
    if(size.width == 0) size.width = element.scrollWidth
    if(size.height == 0) size.height = element.scrollHeight
    return size
  },

  innerSize: function() {
    var size = {}
    size.width = window.innerWidth || 
                   document.documentElement && document.documentElement.clientWidth ||
                   document.body.clientWidth
    size.height = window.innerHeight ||
                   document.documentElement && document.documentElement.clientHeight ||
                   document.body.clientHeight
    return size
  },

  last_size: {width: 0, height: 0},

  onResizeDuringEdit: function() {
    /* keep track of the size from the last resize, because IE likes to call resize over and over
     * even if the window hasn't really resized. */

    var inner_size = windowManager.innerSize()
    if(inner_size.width == windowManager.last_size.width && inner_size.height == windowManager.last_size.height)
      return

    windowManager.last_size = inner_size
    
    var body =  $('mce_editor_0')
    
    if (!body) {
        body  = $('version_body')
        }
        
    var box   = $('edit_box')
    var title = $('version_title')
    
    

    /* the +20 is due to some padding at the bottom of the page that I can't
     * quite figure out how to measure programmatically. */
    var fixed_height = windowManager.offset('col').top +
                       windowManager.size('col').height -
                       windowManager.size(body).height + 20

    /* Due to the shadow on the right of the box, 8 pixels should be enough
     * to compensate (and is, for Safari), but firefox seems to want 3
     * times that number and I can't determine why... */
    var width = windowManager.size(box).width - 8*3

    if(width > 0) {
      body.style.width = width + "px"
      title.style.width = width + "px"
    }

    if(fixed_height < inner_size.height)
      body.style.height = (inner_size.height - fixed_height) + "px"
  }
}

// ===========================================================================
// VERSION MANAGER
// ===========================================================================

var documentManager = {
  toggleChangePassword: function() {
    toggleLink('change_password_link')
    if ($('ChangePassword').style.display == "none") {
      new Effect.BlindDown('ChangePassword', {duration: 0.2})
    } else {
      new Effect.BlindUp('ChangePassword', {duration: 0.2})
    }
    
    scrollWindowTo('ChangePassword')
  },

  onChangePassword: function() {
    Element.show('password_indicator')
  },

  onChangedPassword: function(request) {
    Element.hide('password_indicator')
    if(request.status != 200) {
      flash.show("notice", "The password could not be changed because " + request.responseText)
      Field.focus('password')
    } else {
      flash.show("notice", "The password for this writeboard has been changed.")
      Field.clear('password')
      Field.clear('password_confirmation')
      Element.toggle('ChangePassword')
    }
  }
}

// ===========================================================================
// COMMENT MANAGER
// ===========================================================================
var commentsManager = {
  show: function() {
    toggleLink('add_comment_link')
    toggleElement('NewComment', { afterFinish: function() { scrollWindowTo("Footer") }})
    $('NewComment').className = Element.visible('NewComment') ? 'showing' : ''
    setTimeout("Field.focus('comment_body')", 500)
  },

  hide: function() {
    toggleLink('add_comment_link')
    toggleElement('NewComment')
  },
  
  beforeAdd: function() {
    Element.show('comments_indicator')
  },

  afterAdd: function() {
    Field.clear('comment_body')
    Field.focus('comment_body')
  },

  addCompleted: function(request) {
    toggleLink('add_comment_link')
    Element.hide('comments_indicator', 'NewComment')
    Element.show('comments_header')
    item_id = request.getResponseHeader("Comment-Id")
    $('commentsList').innerHTML = request.responseText
    new Effect.Highlight('comment_' + item_id) 
    setTimeout("$('comment_" + item_id + "').style.background = 'transparent'", 2100)
  },

  trashFromNavigation: function(id) {
    new Effect.Fade('comment_' + id, {afterFinish: function() {
      Element.remove('comment_' + id)
      if($('commentsList').getElementsByTagName('DIV').length < 1) {
        Element.hide('comments_header')
      }
    }})
  }
}

// ===========================================================================
// VERSION MANAGER
// ===========================================================================
versionManager = {
  toggleMinorEdit: function() {
    if ($('commit').value == "Save as the newest version") {
      $('commit').value = 'Save over the current version'
    } else {
      $('commit').value = 'Save as the newest version'
    }
  },

  getSelectedVersions: function(selected) {
    var boxes = new Array()
    var elements = $('compare_form').elements
    boxes.selected_index = -1

    for(var i = 0; i < elements.length; i++)
      if(elements[i].name == "id[]" && elements[i].checked) {
        if(elements[i] == selected) boxes.selected_index = boxes.length
        boxes.push(elements[i])
      }

    return boxes
  },

  ensureSelectedVersions: function() {
    var boxes = this.getSelectedVersions()
    if(boxes.length == 2) return true
    alert("You must select two versions to compare.")
    return false
  },

  checked: function(checkbox) {
    if(!checkbox.checked) {
      $('compare_button').disabled = true
      return
    }

    var selections = this.getSelectedVersions()
    if(selections.length > 2)
      for(var i = 0; i < selections.length; i++)
        if(selections[i] != checkbox) selections[i].checked = false

    this.examineCompareButton()
  },

  examineCompareButton: function() {
    var boxes = this.getSelectedVersions()
    $('compare_button').disabled = (boxes.length != 2)
  },

  toggleFormattingGuide: function() {
    toggleLink('formatting_guide_link_pre')
    toggleLink('formatting_guide_link')
    toggleLink('formatting_guide_link_post')
    toggleElement('formatting_guide')
  }
}

// ===========================================================================
// INVITATION MANAGER
// ===========================================================================
var invitationManager = {
  show: function() {
    toggleLink('invite_link')
    toggleLink('invite_link_extra')

    showElement('InvitePeople', {afterFinish: function() {
      Field.focus('invitation_email_addresses')
    }})
  },
  
  hide: function() {
    toggleLink('invite_link')
    toggleLink('invite_link_extra')

    hideElement('InvitePeople')
  },
  
  toggle: function() {
    Element.visible('InvitePeople') ? this.hide() : this.show()
  },
  
  sending: function() {
    if($('invitation_email_addresses').value.match(/^\s*$/)) {
      alert("Please specify one or more email addresses to invite.")
      return false
    }

    flash.show('progress', 'Sending invitations')
    this.hide()
    return true
  },
  
  sent: function() {
    flash.show('notice', 'Invitations sent')
  }
}

// ===========================================================================
// EXPORT MANAGER
// ===========================================================================
var exportManager = {
  show: function() {
    $('exportButton').src = "/images/b-export-on.gif"
    showElement('download_export')
  },

  hide: function() {
    $('exportButton').src = "/images/b-export.gif"
    hideElement('download_export')
  },

  toggle: function() {
    Element.visible('download_export') ? this.hide() : this.show()
  }
}

// ===========================================================================
// DELIVERY MANAGER
// ===========================================================================
var deliveryManager = {
  show: function() {
    $('deliveryButton').src = "/images/b-email-on.gif"
    showElement('deliver', { afterFinish: function() {
      Field.focus('delivery_email_addresses')
    }})
  },
  
  hide: function() {
    $('deliveryButton').src = "/images/b-email.gif"
    hideElement('deliver')
  },
  
  toggle: function() {
    Element.visible('deliver') ? this.hide() : this.show()
  },
  
  sending: function() {
    if($('delivery_email_addresses').value.match(/^\s*$/)) {
      alert("Please specify one or more email addresses to send this document to.")
      return false
    }

    this.hide()
    flash.show('progress', 'Sending emails')
    return true
  },
  
  sent: function() {
    flash.show('notice', 'Sent emails')
  } 
}

// ===========================================================================
// FLASH
// ===========================================================================
var flash = {
  show: function(type, text) {
    $('flash').className = type
    $('flash').innerHTML = text

    if (type == 'progress') {
      $('flash').innerHTML += "&hellip;"
    }

    if (!Element.visible('flash')) {
      new Effect.Appear('flash')
    }
    
    if (type == 'notice') {
      setTimeout((function() { new Effect.Fade('flash') }).bind(this), 2000);
    }
  }
}
