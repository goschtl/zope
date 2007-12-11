/*
 *  FlashvarSetup.as
 *
 *  Manages the different default settings possible
 *  Also creates a viewport_reset flashvar that contains the reset dimensions
 *
 *  @author <gerold.boehler@lovelysystems.com>
 *
 */

import z3c.reference.imagetool.core.*;
import z3c.reference.imagetool.baseskin.*;

import flash.geom.*;

class z3c.reference.imagetool.baseskin.FlashvarSetup
{
    private var MODE_FIRST_TIME_NO_RATIO:Number = 0;
    private var MODE_FIRST_TIME_WITH_RATIO:Number = 1;
    private var MODE_NORMAL:Number = 2;

    private var VIEWPORT_INITIAL_PERCENT:Number = 1.0;

    private var imageAttitude:EditableImageAttitude;
    private var finalScale:Number = 0;
    //private var viewportRatio:Number = 0;
    private var selectedPreset;
    
	function FlashvarSetup(attitude:EditableImageAttitude)
	{
	    imageAttitude = attitude;
	    finalScale = imageAttitude.originalWidth / imageAttitude.w;
	    var viewportRatio = FlashvarManager.get("crop_w") / FlashvarManager.get("crop_h");
	    
	    selectedPreset = setupPresetList(viewportRatio);
	    
	    if (isMode(MODE_FIRST_TIME_NO_RATIO) || isMode(MODE_FIRST_TIME_WITH_RATIO))
	        initFirstTime();
	    
	    //else if (isMode(MODE_FIRST_TIME_WITH_RATIO))
	    //    initFirstTime();
	    
	    else if (isMode(MODE_NORMAL))
	        initNormal();
        
        // scale down the crop - values
        FlashvarManager.set("crop_x", FlashvarManager.get("crop_x") / finalScale);
        FlashvarManager.set("crop_y", FlashvarManager.get("crop_y") / finalScale);
        FlashvarManager.set("crop_w", FlashvarManager.get("crop_w") / finalScale);
        FlashvarManager.set("crop_h", FlashvarManager.get("crop_h") / finalScale);
	}
	
	public function getSelectedPreset()
	{
	    return selectedPreset;
	}
	
	// preset setup helpers ---------------------------------------------------------
	
	private function setupPresetList(viewportRatio: Number)
	{
        var presetList = createPresetList();
        for (var i = 0; i < presetList.length; i++)
        {
            var preset = presetList[i];
            setupPreset(preset);
        }
        
        var selectedPreset = getPresetByRatio(viewportRatio);
        if (!selectedPreset)
            return presetList[0];
            
        return selectedPreset;
	}
	
	private function createPresetList()
	{
        var presets = FlashvarManager.get("presets");
        var presetList = new Array();

        for (var i in presets)
        {
            var preset = presets[i];
            presetList.unshift(preset);
        }
        
        if (presetList.length > 0)
            FlashvarManager.set("presets", presetList);
            
        return FlashvarManager.get("presets");
	}
	
	private function setupPreset(preset)
	{
	    preset.ratio_x = parseInt(preset.ratio.split(":")[0]);
	    preset.ratio_y = parseInt(preset.ratio.split(":")[1]);
	    preset.ratio = preset.ratio_x / preset.ratio_y;
	    preset.size_x = parseInt(preset.size.split("x")[0]);
	    preset.size_y = parseInt(preset.size.split("x")[1]);
        preset.resetCoords = getViewportFitExtents(preset.ratio);
        preset.resetCoords.x /= finalScale;
        preset.resetCoords.y /= finalScale;
        preset.min_w /= finalScale;
        preset.min_h /= finalScale;
        preset.max_w /= finalScale
        preset.max_h /= finalScale;            
	}
    
    private function getPresetByRatioOrDefault(ratio:Number)
    {
        var preset = getPresetByRatio(ratio);
        if (preset)
            return preset;
        
        return FlashvarManager.get("presets")[0];
    }
	
    // dangerous...
    private function getPresetByRatio(ratio:Number)
    {
        if (isNaN(ratio))
            return null;
            
        var presetList = FlashvarManager.get("presets");
        for (var i = 0; i < presetList.length; i++)
        {
            var preset = presetList[i];
            if (Math.abs(preset.ratio - ratio) < 0.01)
                return preset;
        }
        return null;
    }
    
	// init mode helpers ---------------------------------------------------------
	
    private function isMode(mode:Number)
    {
        switch(mode)
        {
            case MODE_FIRST_TIME_NO_RATIO:
                return FlashvarManager.get("crop_x") < 0 && FlashvarManager.get("crop_y") < 0 && FlashvarManager.get("crop_w") == 0 && FlashvarManager.get("crop_h") == 0;
                break;
                
            case MODE_FIRST_TIME_WITH_RATIO:
                return FlashvarManager.get("crop_x") < 0 && FlashvarManager.get("crop_y") < 0 && FlashvarManager.get("crop_w") > 0 && FlashvarManager.get("crop_h") > 0;
                break;
                
            case MODE_NORMAL:
                return FlashvarManager.get("crop_x") >= 0 && FlashvarManager.get("crop_y") >= 0 && FlashvarManager.get("crop_w") > 0 && FlashvarManager.get("crop_h") > 0;
                break;
        }
        
        return false;
    }
    
    // initFirstTimeNoRatio selects the first preset available and if it has a ratio, applies it
    private function initFirstTime()
    {
        trace("initFirstTime " )

        var ratio = FlashvarManager.get("crop_w") / FlashvarManager.get("crop_h");
        var preset = getPresetByRatioOrDefault(ratio);
    
        if (!preset.ratio)
        {
            FlashvarManager.set("crop_w", imageAttitude.minOriginalSide * VIEWPORT_INITIAL_PERCENT);
            FlashvarManager.set("crop_h", imageAttitude.minOriginalSide * VIEWPORT_INITIAL_PERCENT);
        }
        else
        {
            var imageRatio = imageAttitude.originalWidth / imageAttitude.originalHeight;
            var minSide = (imageAttitude.w < imageAttitude.h) ? imageAttitude.w : imageAttitude.h;
            var dW = imageAttitude.originalWidth - preset.ratio_x;
            var dH = imageAttitude.originalHeight - preset.ratio_y;

            var sign = (dH < 0) ? -1 : 1;   // TODO - why sign???
            var minLen = (sign * (dW / dH) <= sign * imageRatio) ? (imageAttitude.originalWidth) : (imageAttitude.originalHeight * preset.ratio);
            var maxLen = (sign * (dW / dH) >= sign * imageRatio) ? (imageAttitude.originalHeight) : (imageAttitude.originalWidth / preset.ratio);

            FlashvarManager.set("crop_w", minLen);
            FlashvarManager.set("crop_h", maxLen);
        }

        centerViewport();
    }
    /*
    private function initFirstTimeWithRatio()
    {
        trace("initFirstTimeWithRatio")

        var ratio = FlashvarManager.get("crop_w") / FlashvarManager.get("crop_h");
        var preset = getPresetByRatioOrDefault(ratio);

        if (preset.ratio >= 1)
        {
            FlashvarManager.set("crop_w", imageAttitude.minOriginalSide * 0.8);
            FlashvarManager.set("crop_h", imageAttitude.minOriginalSide / preset.ratio * 0.8);
        }
        else
        {
            fitViewportIntoImage(preset.ratio)
        }        

        centerViewport();
    }
    */
    
    private function initNormal()
    {
        trace("initNormal")
        var ratio = FlashvarManager.get("crop_w") / FlashvarManager.get("crop_h");
        var currentPreset = getPresetByRatio(ratio);
        
        // if there is no preset with this name, change to the default preset but leave the crop area as is
        if (!currentPreset)
        {
            currentPreset = getPresetByRatioOrDefault();
            //fitViewportIntoImage(currentPreset.ratio);
            //centerViewport();
        }
    }
    
    // viewport helpers ---------------------------------------------------------
    /*
    private function fitViewportIntoImage(viewportRatio:Number)
    {
        var resetExtents = getViewportFitExtents(viewportRatio);
        
        FlashvarManager.set("crop_w", resetExtents.x);
        FlashvarManager.set("crop_h", resetExtents.y);
    }
    */
    
    private function getViewportFitExtents(viewportRatio:Number)
    {
        if (isNaN(viewportRatio))
            return new Point(imageAttitude.minOriginalSide * VIEWPORT_INITIAL_PERCENT, imageAttitude.minOriginalSide * VIEWPORT_INITIAL_PERCENT);
            
        /*
        var minLen = imageAttitude.minOriginalSide;
        var viewportW = imageAttitude.originalWidth * 0.8;
        var viewportH = imageAttitude.originalHeight * 0.8;
        var minLen = (viewportW > viewportH) ? viewportH : viewportW;
        */
        
        if (viewportRatio >= 1)
            return new Point(imageAttitude.minOriginalSide * VIEWPORT_INITIAL_PERCENT, imageAttitude.minOriginalSide * VIEWPORT_INITIAL_PERCENT / viewportRatio);
            
        return new Point(imageAttitude.minOriginalSide * VIEWPORT_INITIAL_PERCENT * viewportRatio, imageAttitude.minOriginalSide * VIEWPORT_INITIAL_PERCENT);
    }
    
    private function centerViewport()
    {
        FlashvarManager.set("crop_x", (imageAttitude.originalWidth - FlashvarManager.get("crop_w")) / 2)
        FlashvarManager.set("crop_y", (imageAttitude.originalHeight - FlashvarManager.get("crop_h")) / 2)
    }    
}