/* Some help functions */

function getBetterElementsByClassName(class_name)
  /* A better implementation that works in IE 5.5 */
  {
    var all_obj,ret_obj=new Array(),j=0,teststr;

    if(document.all)all_obj=document.all;
    else if(document.getElementsByTagName && !document.all)
      all_obj=document.getElementsByTagName("*");

    for(i=0;i<all_obj.length;i++)
    {
      if(all_obj[i].className.indexOf(class_name)!=-1)
      {
        teststr=","+all_obj[i].className.split(" ").join(",")+",";
        if(teststr.indexOf(","+class_name+",")!=-1)
        {
          ret_obj[j]=all_obj[i];
          j++;
        }
      }
    }
    return ret_obj;
  }
      
document.getElementsByClassName = getBetterElementsByClassName;


