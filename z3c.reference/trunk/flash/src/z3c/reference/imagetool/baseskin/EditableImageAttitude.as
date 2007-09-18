/**
* z3c.reference.imagetool.baseskin.EditableImageAttitude 
* makes animated rotations around the center of the mc
* 
*
* @author <gerold.boehler@lovelysystems.com>
*/

import z3c.reference.imagetool.core.*;

import com.robertpenner.easing.*;
import de.alex_uhlmann.animationpackage.animation.Rotation;


[Event("onImageRotated")]


class z3c.reference.imagetool.baseskin.EditableImageAttitude extends z3c.reference.imagetool.baseskin.MovieclipAttitude
{
    private var nextDegree:Number = 0;
    private var animRotate:Rotation;
    
    function EditableImageAttitude(mc_:MovieClip)
    {
        super();

	    animRotate = new Rotation(mc_);
	    animRotate.addEventListener("onEnd", this);
        animRotate.animationStyle(500, Sine.easeInOut);
    }
    
    public function rotateLeft()
    {
        if (animRotate.isTweening())
            return;

        if (nextDegree == 0 || nextDegree == 180)
		    animRotate.setRegistrationPoint({position:"CENTER"});

        nextDegree -= 90;
        animRotate.run(nextDegree);
    }
    
    public function rotateRight()
    {
        if (animRotate.isTweening())
            return;
        
        if (nextDegree == 0 || nextDegree == 180)
		    animRotate.setRegistrationPoint({position:"CENTER"});

        nextDegree += 90;
        animRotate.run(nextDegree);
    }
    
    public function rotate(degrees:Number)
    {
        if (animRotate.isTweening())
            return;
        
        var r = degrees % 360;
        
        if (r == 0)
            r = 0;
        if (r == 90)
        {
	        animRotate.setRegistrationPoint({position:"CENTER"});
            r = -90;
        }
        else if (r == -90)
        {
	        animRotate.setRegistrationPoint({position:"CENTER"});
            r = 90;
        }
        else if (r == 180 || r == -180)
            r = 180;
        else if (r == 270 || r == -270)
        {
	        animRotate.setRegistrationPoint({position:"CENTER"});
            r = 90;
        }

        nextDegree = r;
        animRotate.run(r);
    }
    
    public function get r():Number
    {
        if (nextDegree == -90)
            return 90;
            
        if (nextDegree == 90)
            return 270;
            
        return nextDegree;
    }
    
    // event listeners -----------------------------------------------
    
    function onEnd(eo:Object)
    {
        switch(nextDegree)
        {
            case 0:
                mc._rotation = 0;
                break;
                
            case 90:
                break;
                
            case -180:
                mc._rotation = 180;
                nextDegree = 180;
                break;
                
            case 270:
                mc._rotation = -90;
                nextDegree = -90;
                break;
        }

        // don't forget to call updatePosition after a rotation
        updatePosition();
                
        var ei:EventInfo = new EventInfo(this, "onImageRotated");
        broadcastEvent(ei);
    }

    // helpers --------------------------------------------------------
    
}