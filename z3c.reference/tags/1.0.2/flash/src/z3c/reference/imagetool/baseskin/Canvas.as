/*
 *  the visual representation of the paintable area
 *
 *  @author <gerold.boehler@lovelysystems.com>
 */

import z3c.reference.imagetool.core.*;
import z3c.reference.imagetool.baseskin.*;


class z3c.reference.imagetool.baseskin.Canvas extends Component
{
    private var width:Number = 1;
    private var height:Number = 1;
    
    private var border_mc:MovieClip;
    private var mask_arr:Array;
    
	function Canvas()
	{
        super();
        
        createEmptyMovieClip("border_mc", getNextHighestDepth());
        mask_arr = new Array();
        
        var shadow = new flash.filters.DropShadowFilter(3);
        filters = [shadow];
    }
    
    public function onParentResize(w:Number, h:Number)
    {
        width = w;
        height = h;
        
        border_mc.clear();
        border_mc.lineStyle(0, 0x000000, 100);
        border_mc.beginFill(0xffffff, 100);
        border_mc.moveTo(0, 0);
        border_mc.lineTo(width, 0);
        border_mc.lineTo(width, height);
        border_mc.lineTo(0, height);
        border_mc.endFill();

        for (var i = 0; i < mask_arr.length; i++)
        {
            var mask_mc = mask_arr[i];
            mask_mc.clear();
            mask_mc.lineStyle(0, 0x000000, 100);
            mask_mc.beginFill(0x000000, 0);
            mask_mc.moveTo(1, 1);
            mask_mc.lineTo(width, 1);
            mask_mc.lineTo(width, height);
            mask_mc.lineTo(1, height);
            mask_mc.endFill();
        }
    }
    
    public function getMask()
    {
        var nextDepth = getNextHighestDepth();
        var mask_mc = createEmptyMovieClip("mask_mc_" + nextDepth, nextDepth);
        mask_arr.push(mask_mc);
        
        return mask_mc;
    }

    // event listeners --------------------------------------------------------------
    
    // helpers ----------------------------------------------------------------------
    
}
