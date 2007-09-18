/**
* z3c.reference.imagetool.baseskin.MovieclipAttitude 
* helper class to get the coordinates and dimensions in global space for a specified movieclip
* makes sure we get the global width and heights for rotated movieclips
* converts funny flash rotations to 'normal' rotations (0, 90, 180, 270) / (0, -90, -180, -270)
* 
* extends EventBroadcaster so that subclasses can fire events if they need to
*
* @author <gerold.boehler@lovelysystems.com>
*/

class z3c.reference.imagetool.baseskin.MovieclipAttitude extends z3c.reference.imagetool.core.EventBroadcaster
{
    private var mX:Number = 0;
    private var mY:Number = 0;
    private var mW:Number = 1;
    private var mH:Number = 1;
    private var mIw:Number = 1;
    private var mIh:Number = 1;
    private var mOw:Number = 1;
    private var mOh:Number = 1;
    private var mR:Number = 0;  // in flash rotations
    
    private var mc:MovieClip;
    
    function MovieclipAttitude()
    {
        super();
    }
    
    // only used to remember the original dimensions
    public function setOriginalSize(w:Number, h:Number)
    {
        mOw = w;
        mOh = h;
    }
    
    // important: pass the mc without rotations applied!!!
    public function setTarget(mc_:MovieClip)
    {
        mc = mc_;
        mX = mc._x;
        mY = mc._y;
        mW = mc._width;
        mH = mc._height;
        mIw = mW;
        mIh = mH;

        updatePosition();
    }
    
    public function set x(value:Number)
    {
        if (mc._rotation == 0 || mc._rotation == -90)
            mc._x = value;
        else if (mc._rotation == 180 || mc._rotation == 90)
            mc._x = value + w;
            
        updatePosition();
    }
    
    public function set y(value:Number)
    {
        if (mc._rotation == 0 || mc._rotation == 90)
            mc._y = value;
        else if (mc._rotation == 180 || mc._rotation == -90)
            mc._y = value + h;
            
        updatePosition();
    }
    
    public function set r(value:Number)
    {
        mR = value % 360;
        
        if (mR == 0)
            mc._rotation = 0;
        if (mR == 90)
            mc._rotation = -90;
        else if (mR == -90)
            mc._rotation = 90;
        else if (mR == 180 || mR == -180)
            mc._rotation = 180;
        else if (mR == 270 || mR == -270)
            mc._rotation = -mR;
            
        updatePosition();
    }
    
    public function get w():Number
    {
        if (mc._rotation == 0 || mc._rotation == 180)
            return mW;
        else if (mc._rotation == 90 || mc._rotation == -90)
            return mH;
            
        return 1;
    }

    public function get h():Number
    {
        if (mc._rotation == 0 || mc._rotation == 180)
            return mH;
        else if (mc._rotation == 90 || mc._rotation == -90)
            return mW;
            
        return 1;
    }
    
    public function set w(value:Number)
    {
        var rot = mc._rotation;
        mc._rotation = 0;
        if (rot == 0 || rot == 180)
        {
            mW = value;
            mc._width = mW;
        }
        else if (rot == 90 || rot == -90)
        {
            mH = value;
            mc._height = mH;
        }
        mc._rotation = rot;
        
        updatePosition();
    }
    
    public function set h(value:Number)
    {
        var rot = mc._rotation;
        mc._rotation = 0;
        if (rot == 0 || rot == 180)
        {
            mH = value;
            mc._height = mH;
        }
        else if (rot == 90 || rot == -90)
        {
            mW = value
            mc._width = mW;
        }
        mc._rotation = rot;
        
        updatePosition();
    }
    
    public function get x():Number
    {
        return mX;
    }

    public function get y():Number
    {
        return mY;
    }
    
    public function get initialWidth():Number
    {
        if (mc._rotation == 0 || mc._rotation == 180)
            return mIw;
        else if (mc._rotation == 90 || mc._rotation == -90)
            return mIh;
    }
    
    public function get initialHeight():Number
    {
        if (mc._rotation == 0 || mc._rotation == 180)
            return mIh;
        else if (mc._rotation == 90 || mc._rotation == -90)
            return mIw;
    }
    
    public function get originalWidth():Number
    {
        if (!mc)
            return mOw;
        else if (mc._rotation == 0 || mc._rotation == 180)
            return mOw;
        else if (mc._rotation == 90 || mc._rotation == -90)
            return mOh;
    }
    
    public function get originalHeight():Number
    {
        if (!mc)
            return mOh;
        else if (mc._rotation == 0 || mc._rotation == 180)
            return mOh;
        else if (mc._rotation == 90 || mc._rotation == -90)
            return mOw;
    }
    
    public function get originalRatio():Number
    {
        return originalWidth / originalHeight;
    }
    
    public function get r():Number
    {
        return mR;
    }

    // helpers ---------------------------------------------------------------

    private function updatePosition()
    {
        if (mc._rotation == 0)
        {
            mX = mc._x;
            mY = mc._y;
        }
        else if (mc._rotation == 180)
        {
            mX = mc._x - w;
            mY = mc._y - h;
        }
        else if (mc._rotation == -90)
        {
            mX = mc._x;
            mY = mc._y - h;
        }
        else if (mc._rotation == 90)
        {
            mX = mc._x - w;
            mY = mc._y;
        }
    }
    
    public function toString()
    {
        return " x: " + x + " y: " + y + " w: " + w + " h: " + h + " r: " + r;
    }
}