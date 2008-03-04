/*
 *  the slider for zooming the image
 *
 *  @author <gerold.boehler@lovelysystems.com>
 */

import z3c.reference.imagetool.core.*;
import z3c.reference.imagetool.baseskin.*;


[Event("onSliderPress")]
[Event("onSliderRelease")]
[Event("onSliderChange")]


class z3c.reference.imagetool.baseskin.Slider extends Component
{
    private var line_mc:MovieClip;
    private var button_mc:MovieClip;

    private var maxLength:Number = 0;
    private var currentPercent:Number = 0;
    
    // from attachMovie
    private var width:Number = 1;
    
	function Slider()
	{
        super();
        
        createEmptyMovieClip("line_mc", getNextHighestDepth());
        line_mc.clear();
        line_mc.lineStyle(0, 0x000000, 100);
        line_mc.moveTo(0, 0);
        line_mc.lineTo(width, 0);
        line_mc.endFill();
        line_mc._y = 6;

        createEmptyMovieClip("button_mc", getNextHighestDepth());
        button_mc.clear();
        button_mc.beginFill(0xc0c0c0, 100);
        button_mc.moveTo(0, 0);
        button_mc.lineTo(12, 0);
        button_mc.lineTo(12, 12);
        button_mc.lineTo(0, 12);
        button_mc.endFill();
        button_mc._y = 0;
        
        maxLength = width - button_mc._width;

        button_mc.onPress = function() { _parent.onButtonPress(); }
        button_mc.onRelease = button_mc.onReleaseOutside = function() { _parent.onButtonRelease(); }
        
        var shadow = new flash.filters.DropShadowFilter(1);
        filters = [shadow];
    }
    
    public function setPercent(percent:Number)
    {
        button_mc._x = 0;
        dragSlider();
    }
    
    function onButtonPress()
    {
        button_mc.startDrag(false, 0, 0, width - button_mc._width, 0)
        onEnterFrame = dragSlider;

        var ei:EventInfo = new EventInfo(this, "onSliderPress");
        ei.setInfo("percent", currentPercent);
        broadcastEvent(ei);
    }
    
    function onButtonRelease()
    {
        dragSlider();
        button_mc.stopDrag();
        onEnterFrame = null;

        var ei:EventInfo = new EventInfo(this, "onSliderRelease");
        ei.setInfo("percent", currentPercent);
        broadcastEvent(ei);
    }
    
    function dragSlider()
    {
        var nextPercent = button_mc._x / maxLength;
        if (nextPercent == currentPercent)
            return;
            
        currentPercent = nextPercent;
        var ei:EventInfo = new EventInfo(this, "onSliderChange");
        ei.setInfo("percent", currentPercent);
        broadcastEvent(ei);
    }
}
