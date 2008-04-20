r += '''
<script type="text/javascript">
  Ext.onReady(function(){
'''

for viewlet in context.viewlets:
    r += viewlet.render()

r += '''
  });
</script>
'''
