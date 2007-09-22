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
[Event("onSliderPress")]
[Event("onSliderRelease")]
[Event("onSliderChange")]
[Event("onViewportRatioChange")]


class z3c.reference.imagetool.baseskin.Controller extends Component
{
    private var PADDING:Number = 20;
    
	public var buttons_mc:MovieClip;
	private var rotateLeft_mc:MovieClip;
	private var rotateRight_mc:MovieClip;
	private var slider_mc:MovieClip;
	private var outputsize_mc:MovieClip;
	private var canvas_mc:MovieClip;

	private var dropdown_container_mc:MovieClip;    // contains the dropdown component
	private var dropdown_mc:MovieClip;              // reference to the dropdown component
	
	
	function Controller()
	{
	    attachMovie("canvas_mc", "canvas_mc", getNextHighestDepth());
	    createEmptyMovieClip("buttons_mc", getNextHighestDepth());
	    buttons_mc.setMask(canvas_mc.getMask());
		
		rotateLeft_mc = buttons_mc.attachMovie("rotateLeft_mc", "rotateLeft_mc", buttons_mc.getNextHighestDepth());
		rotateLeft_mc.onRelease = rotateLeft_mc.onReleaseOutside = function() { _parent._parent.broadcastEvent(new EventInfo(_parent._parent, "onRotateLeftRelease")); }

		rotateRight_mc = buttons_mc.attachMovie("rotateRight_mc", "rotateRight_mc", buttons_mc.getNextHighestDepth());
		rotateRight_mc.onRelease = rotateRight_mc.onReleaseOutside = function() { _parent._parent.broadcastEvent(new EventInfo(_parent._parent, "onRotateRightRelease")); }
		
		slider_mc = buttons_mc.attachMovie("slider_mc", "slider_mc", buttons_mc.getNextHighestDepth(), {width: 100});
		slider_mc.addListener(this);
		
		dropdown_container_mc = _level0.dropdown_mc;
		dropdown_mc = dropdown_container_mc.attachMovie("ComboBox", "dropdown_mc", dropdown_container_mc.getNextHighestDepth());
        dropdown_mc.setSize(150, dropdown_mc._height);        		
		dropdown_mc._visible = false;
	}
	
	public function init()
	{
	    var presets = FlashvarManager.get("presets");
	    if (!presets)
            return;
            
        dropdown_mc.setStyle("fontFamily", "Arial");
        dropdown_mc.setStyle("fontSize", 11);
        dropdown_mc.setStyle("themeColor", 0xc0c0c0)
        dropdown_mc.setStyle("openDuration", 0);
        dropdown_mc.setStyle("openEasing", null);
        dropdown_mc.setStyle("selectionDuration", null);
        dropdown_mc.setStyle("selectionEasing", null);
        //dropdown_mc.setStyle("useRollOver", false);
        dropdown_mc.setStyle("textSelectedColor", 0x000000)
        dropdown_mc.setStyle("rollOverColor", 0xdddddd);

        //dropdown_mc.setStyle("rollOverColor", 0xe8e8e8);
        //dropdown_mc.setStyle("textRollOverColor", 0x333333);
        //dropdown_mc.setStyle("selectionColor", 0xe8e8e8);
        //dropdown_mc.setStyle("textSelectedColor", 0x333333);
        //dropdown_mc.setStyle("embedFonts", true);
        
		dropdown_mc.rowCount = 10;
        dropdown_mc.addEventListener("change", this);
        
        var selectedItem = presets[0];
        for (var i = 0; i < presets.length; i++)
        {
            var item = presets[i];
            dropdown_mc.addItem({label: item.name, data: item});
            if (item.selected)
            {
                dropdown_mc.selectedIndex = i;
                selectedItem = item;
            }
        }
        
        dropdown_mc._visible = presets.length > 1;

        log("SELECTED: " + selectedItem.name)
        fireRatioChange(selectedItem);
	}
	
	// event listeners ----------------------------------------------------------------
	
	// forward slider events
	function onSliderChange(ei:EventInfo)
	{
	    broadcastEvent(ei);
	}

	function onSliderPress(ei:EventInfo)
	{
	    broadcastEvent(ei);
	}

	function onSliderRelease(ei:EventInfo)
	{
	    broadcastEvent(ei);
	}
	
	// forward dropdown events
    private function change(obj:Object)
    {
        fireRatioChange(obj.target.selectedItem.data);
    }
    
    private function fireRatioChange(item:Object)
    {
        var ei:EventInfo = new EventInfo(this, "onViewportRatioChange");
        ei.setInfo("preset", item);
        broadcastEvent(ei);
    }
    
    function onFitImage(ei:EventInfo)
    {
        slider_mc.setPercent(0);
    }
	
	public function onParentResize(w:Number, h:Number)
	{
	    var centerY = h / 2;

	    canvas_mc._x = 0;
	    canvas_mc._y = 0;
	    canvas_mc.onParentResize(w, h);

	    // left alligned
	    var nextX = PADDING;
	    
    	rotateLeft_mc._x = nextX;
    	rotateLeft_mc._y = centerY - rotateLeft_mc._height / 2;
    	nextX += rotateLeft_mc._width + PADDING;
    	
    	rotateRight_mc._x = nextX;
    	rotateRight_mc._y = centerY - rotateRight_mc._height / 2;
    	nextX += rotateRight_mc._width + PADDING;

    	
    	// right alligned
    	if (FlashvarManager.get("presets").length > 1)
    	{
        	nextX = w - dropdown_mc._width - PADDING;    	
    		dropdown_mc._y = Stage.height - 44;
    		dropdown_mc._x = Stage.width - 20 - dropdown_mc._width;
        	nextX = dropdown_mc._x - PADDING - slider_mc._width;
    	}
        else
        {
            nextX = w - slider_mc._width - PADDING;
        }
        
    	slider_mc._x = nextX;
    	slider_mc._y = centerY - slider_mc._height / 2;
    	
    	nextX = slider_mc._x - PADDING; //- ???
	}
}