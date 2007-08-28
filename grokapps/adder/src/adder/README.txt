This is the simplest Grok app we could think that is still useful:
an adding machine with tape. 

It's so simple that it's only model class derives from grok.Model, and not
from grok.Container. The terms of the sum are saved in a PersistenList.
