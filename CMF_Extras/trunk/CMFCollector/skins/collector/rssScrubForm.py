##Script (Python) "rssScrubForm"
##title=Scrub form of useless variables
##parameters=form
result = form.copy()
if '-C' in result:
    del result['-C']

if 'searching' in result:
    del result['searching']

empty = []
for k, v in result.items():
    if not v:
        empty.append(k)

for k in empty:
    del result[k]

return result
