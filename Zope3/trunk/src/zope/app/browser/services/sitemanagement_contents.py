<html metal:use-macro="views/standard_macros/page">
<head>
<style metal:fill-slot="headers" type="text/css">
</style>
</head>
<body>
<div metal:fill-slot="body">

<form action="." method="get" 
      tal:define="container_contents view/listContentInfo"
>

  <p>Package Contents</p>

  <div metal:use-macro="view/contentsMacros/macros/contents_table" />

  <br />
    <input type="text" name="name" />
    <input type="submit" name="@@addPackage.html:method" value="Add"
           i18nXXX:attributes="value string:menu_add_button" />
    <input type="submit" name="@@removeObjects.html:method" value="Delete"
           i18nXXX:attributes="value string:menu_delete_button" /> 
</form>

</div>
</body>
</html>
