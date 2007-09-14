/**
* Class z3c.reference.imagetool.baseskin.Controller
* Menu - Class of the Flash ImageCrop Tool
* 
* @author viktor.sohm@lovelysystems.com
* @author gerold.boehler@lovelysystems.com
*/

import z3c.reference.imagetool.core.*;


[Event("onZoomInPress")]
[Event("onZoomInRelease")]
[Event("onZoomOutPress")]
[Event("onZoomOutRelease")]
[Event("onRotateLeftRelease")]
[Event("onRotateRightRelease")]
[Event("onAcceptRelease")]
[Event("onAbortRelease")]


class z3c.reference.imagetool.baseskin.Controller extends Component
{
    private var PADDING:Number = 20;
    
	private var menuDrag_mc:MovieClip;
	private var zoomIn_mc:MovieClip;
	private var zoomOut_mc:MovieClip;
	private var rotateLeft_mc:MovieClip;
	private var rotateRight_mc:MovieClip;
	private var menuAbort_mc:MovieClip;
	private var menuAccept_mc:MovieClip;
	private var cropsize_mc:MovieClip; //movieclip holding the textfields for manual size input
	private var outputsize_mc:MovieClip;
	
	private var bg_mc:MovieClip;
	
	function Controller()
	{
		trace("Menu Initialized");
		
		bg_mc._width=Stage.width;
		bg_mc._height=50;
		var shadow = new flash.filters.DropShadowFilter(3);
        bg_mc.filters = [shadow];

		menuDrag_mc.onPress = function() { _parent.startDrag(false); }		
		menuDrag_mc.onRelease = function() { _parent.stopDrag(); }
		
		zoomIn_mc.onPress = function() { _parent.broadcastEvent(new EventInfo(_parent, "onZoomInPress")); }
		zoomIn_mc.onRelease =  this.zoomIn_mc.onReleaseOutside = function() { _parent.broadcastEvent(new EventInfo(_parent, "onZoomInRelease")); }
		
		zoomOut_mc.onPress = function() { _parent.broadcastEvent(new EventInfo(_parent, "onZoomOutPress")); }
		zoomOut_mc.onRelease = this.zoomOut_mc.onReleaseOutside = function() { _parent.broadcastEvent(new EventInfo(_parent, "onZoomOutRelease")); }
		
		rotateLeft_mc.onRelease = function() { _parent.broadcastEvent(new EventInfo(_parent, "onRotateLeftRelease")); }
		rotateRight_mc.onRelease = function() { _parent.broadcastEvent(new EventInfo(_parent, "onRotateRightRelease")); }
		
		menuAccept_mc.onRelease = function() { _parent.broadcastEvent(new EventInfo(_parent, "onAcceptRelease")); }
		menuAbort_mc.onRelease = function() { _parent.broadcastEvent(new EventInfo(_parent, "onAbortRelease")); }
		
	/*	
		this.cropsize_mc.width_txt.ptr=this.pointer;
		this.cropsize_mc.width_txt.onChanged=function() {
		    //trace("width was changed: " + this.text);
		    this.ptr.onManualCropSizeChange(this.text, this._parent.height_txt.text);
		}
		this.cropsize_mc.height_txt.ptr=this.pointer; 
		this.cropsize_mc.height_txt.onChanged=function(){
		    this.ptr.onManualCropSizeChange(this._parent.width_txt.text, this.text);
		}
		
		this.outputsize_mc.width_txt.ptr=this.pointer;
		this.outputsize_mc.width_txt.onChanged=function() {
		    //trace("width was changed: " + this.text);
		    this.ptr.onManualOutputSizeChange(this.text, this._parent.height_txt.text);
		}
		this.outputsize_mc.height_txt.ptr=this.pointer; 
		this.outputsize_mc.height_txt.onChanged=function(){
		    this.ptr.onManualOutputSizeChange(this._parent.width_txt.text, this.text);
		}
	*/	
	}
	
	function setCropSizeValues(width:Number, height:Number) {
	    this.cropsize_mc.width_txt.text=width;
	    this.cropsize_mc.height_txt.text=height;
	}
	function updateOutputSizeValues(width:Number, height:Number) {
	    this.outputsize_mc.width_txt.text=width;
	    this.outputsize_mc.height_txt.text=height;
	}
	
	public function onParentResize(w:Number, h:Number)
	{
	    bg_mc._width = w
	    bg_mc._height = h;
	    
	    var nextX = PADDING;
	    var centerY = h / 2;
	    
    	rotateLeft_mc._x = nextX;
    	rotateLeft_mc._y = centerY - rotateLeft_mc._height / 2;
    	nextX += rotateLeft_mc._width + PADDING;
    	
    	rotateRight_mc._x = nextX;
    	rotateRight_mc._y = centerY - rotateRight_mc._height / 2;
    	nextX += rotateRight_mc._width + PADDING;

    	zoomIn_mc._x = nextX;
    	zoomIn_mc._y = centerY - zoomIn_mc._height / 2;
    	nextX += zoomIn_mc._width + PADDING;

    	zoomOut_mc._x = nextX;
    	zoomOut_mc._y = centerY - zoomOut_mc._height / 2;
    	nextX += zoomOut_mc._width + PADDING;

    	menuAccept_mc._x = nextX;
    	menuAccept_mc._y = centerY - menuAccept_mc._height / 2;
    	nextX += menuAccept_mc._width + PADDING;

    	menuAbort_mc._x = nextX;
    	menuAbort_mc._y = centerY - menuAbort_mc._height / 2;
    	nextX += menuAbort_mc._width + PADDING;
	}
}