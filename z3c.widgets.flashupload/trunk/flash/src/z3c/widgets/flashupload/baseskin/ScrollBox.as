/**
    Simple textbox with scrollers to display the list of items that were too big
    to be uploaded

    @author <gerold.boehler@lovelysystems.com>
*/


class z3c.widgets.flashupload.baseskin.ScrollBox extends MovieClip
{
    private var headline_txt:TextField;
    private var list_txt:TextField;
    
    private var bg_mc:MovieClip;
    private var up_mc:MovieClip;
    private var down_mc:MovieClip;
    
    private var width:Number;
    private var height:Number;
    
    public function ScrollBox()
    {
        super();
        
        attachMovie("up_mc", "up_mc", getNextHighestDepth());
        up_mc.onPress = function() { _parent.onUpPress(); }
        up_mc.onRelease = function() { _parent.onUpRelease(); }
        
        attachMovie("down_mc", "down_mc", getNextHighestDepth())
        down_mc.onPress = function() { _parent.onDownPress(); }
        down_mc.onRelease = function() { _parent.onDownRelease(); }
        
        headline_txt.autoSize = true;
        headline_txt.text = "";
        list_txt.text = "";
    }
    
    public function setHeadline(txt:String)
    {
        headline_txt.text = txt;
    }
    
    public function setText(txt:String)
    {
        list_txt.text = txt;
        onActivity();
    }
    
    public function addText(txt:String)
    {
        list_txt.text += txt;
        onActivity();
    }
    
    public function getText():String
    {
        return list_txt.text;
    }
    
    private function onActivity()
    {
        up_mc._visible = list_txt.scroll > 1;
        down_mc._visible = list_txt.scroll < list_txt.maxscroll;
        
        if (!up_mc._visible && !down_mc._visible)
        {
            bg_mc._width = width;
            list_txt._width = width;
        }
        else
        {
            bg_mc._width = width - 20;
            list_txt._width = width - 20;
        }
    }
    
    // event listeners --------------------------------------------------------
    
    function onUpPress()
    {

    }
    
    function onUpRelease()
    {
        if (list_txt.scroll == 1)
            return;
            
        list_txt.scroll--;
        onActivity();
    }
    
    function onDownPress()
    {
        
    }
    
    function onDownRelease()
    {
        if (list_txt.scroll == list_txt.maxscroll)
            return;
            
        list_txt.scroll++;
        onActivity();
    }

    private function onParentResize(w:Number, h:Number)
    {
        width = w;
        height = h;
        
        headline_txt._x = 0;
        headline_txt._y = 0;
        headline_txt._width = w;
        headline_txt._height = h;
        
        bg_mc._x = 0;
        bg_mc._y = 18;
        bg_mc._width = w - 20;
        bg_mc._height = h - 18;
        
        list_txt._x = 0;
        list_txt._y = bg_mc._y;
        list_txt._width = bg_mc._width;
        list_txt._height = bg_mc._height;
        
        up_mc._x = w - up_mc._width;
        up_mc._y = bg_mc._y;
        
        down_mc._x = w - up_mc._width;
        down_mc._y = h - down_mc._height;
        
        onActivity();
    }
    
    // helpers ------------------------------------------------------------------------
    
    public function log(msg):Void{
        trace(msg);
		
		if (msg.length>500) msg = msg.substring(msg.length-100, msg.length);
		
        _level0.debug_txt.text+=msg+"\n";
		_level0.debug_txt.scroll = _level0.debug_mc.debug_txt.maxscroll;
    }

}
