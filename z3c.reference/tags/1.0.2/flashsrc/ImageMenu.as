/**
* Class ImageMenu
* Menu - Class of the Flash ImageCrop Tool
* 
* @author viktor.sohm@lovelysystems.com
*/

class ImageMenu extends MovieClip {
	
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
	
	public var pointer;
	
	private var _eObj:Object;
	private var _eFunc:Object;
	private var _eArgs:Array;
	
	/**
	* Initializes the functions of the Menu Icons and defines the menu Position
	*/
	function ImageMenu(){
		trace("Menu Initialized");
	}
	
	public function init(){
		
		bg_mc._width=Stage.width;
		bg_mc._height=50;
		this._y=Stage.height-50;
		
		
		this.zoomOut_mc.pointer = this.pointer;
		this.zoomOut_mc.mn = this;
		
		this.zoomIn_mc.pointer = this.pointer;
		this.zoomIn_mc.mn = this;
		
		this.rotateLeft_mc.pointer = this.pointer;
		this.rotateLeft_mc.mn = this;
		
		this.rotateRight_mc.pointer = this.pointer;
		this.rotateRight_mc.mn = this;
		
		this.menuAbort_mc.pointer = this.pointer;
		this.menuAbort_mc.mn = this;
		
		this.menuAccept_mc.pointer = this.pointer;
		this.menuAccept_mc.mn = this;
		
		
		/**
		* Defines what happens when you press on the Drag Field (draggin of menu starts)
		*/
		this.menuDrag_mc.onPress = function(){
			this._parent.startDrag(false);
		}
		
		/**
		* Defines waht happens when you release the Drag Field (drag stops)
		*/
		this.menuDrag_mc.onRelease = function(){
			this._parent.stopDrag();
		}
		
		/**
		* Zoom In Event
		*/
		this.zoomIn_mc.onPress = function(){
			this.mn.triggerOnEnterFrame(this.pointer, this.pointer.onZoomClicked, 1, 2);
		}
		this.zoomIn_mc.onRelease =  this.zoomIn_mc.onReleaseOutside = function() {
	        this.mn.releaseOnEnterFrame();
	    }
		
		/**
		* Zoom out Event
		*/
		this.zoomOut_mc.onPress = function(){
			this.mn.triggerOnEnterFrame(this.pointer, this.pointer.onZoomClicked, -1, 2);
		}
		this.zoomOut_mc.onRelease = this.zoomOut_mc.onReleaseOutside = function() {
			this.mn.releaseOnEnterFrame();
		}
		
		/**
		* Rotate Left Button Event
		*/
		this.rotateLeft_mc.onRelease = function(){
			this.pointer.onRotateClicked(-1);
		}
		
		/**
		* Rotate Right Button Event
		*/
		this.rotateRight_mc.onRelease = function(){
			this.pointer.onRotateClicked(1);
		}
		
		/**
		* Reset / Abort Events
		*/
		this.menuAbort_mc.onRelease = function(){
            // currently abused for testing!!!!!!
			this.pointer.switchMode();
		}
		
		/**
		* Accept Event
		*/
		this.menuAccept_mc.onRelease = function(){
			this.pointer.saveChanges();
		}
		
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
	
	private function triggerOnEnterFrame(eo:Object, ef:Function) {
	    _eObj=eo;
	    _eFunc=ef;
	    _eArgs=arguments.slice(2);
	    onEnterFrame=enterFrame;
	}
	
	private function releaseOnEnterFrame() {
	    
	    trace("releasing Enterframe");
	    
	    _eObj=null;_eFunc=null;_eArgs=null
	    onEnterFrame=null;
	}
	
	private function enterFrame() {
	    _eFunc.apply(_eObj, _eArgs);
	} 


}